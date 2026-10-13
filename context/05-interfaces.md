# Interfaces entre trilhas (contratos de integração)

> **Para que serve:** permitir o desenvolvimento **assíncrono**. Cada trilha produz e
> consome os artefatos abaixo **exatamente** neste formato. Enquanto o produtor real não
> está pronto, o consumidor usa os dados sintéticos/mocks (seção "Como não ficar travado").
>
> **Regra:** estas interfaces estão **congeladas**. Para mudar, abra um PR alterando este
> arquivo, marque as trilhas afetadas e só faça merge com o OK delas.

## Mapa produtor → consumidor

| Artefato | Produz (trilha) | Consome (trilha) | Mock enquanto não existe |
|---|---|---|---|
| `data/reference/reference.parquet` | A (T1.2) | B, C | `make_synthetic_credit_df()` (C, T0.5) |
| `data/production/production_base.parquet` | A (T1.2) | C | `make_synthetic_credit_df()` (C, T0.5) |
| `contracts.validate_or_block()` | A (T1.5) | B (T2.4) | chamar `schema.validate()` direto |
| `models/baseline_v1.joblib` | B (T1.8) | B (T2.4), C (T2.6) | coluna `score` sintética (C, T0.5) |
| `reports/training/feature_importance.csv` | B (T1.9) | B (T4.3), C (T2.1) | rascunho do YAML de cenários |
| `data/production/<janela>.parquet` | C (T2.3) | B (T2.4), C (T2.6) | `make_synthetic_window()` (C, T0.5) |
| `logs/predictions.jsonl` | B (T2.4) | D (T3.2) | `tests/fixtures/mocks/` (T3.0) |
| `logs/validation.jsonl` | A (T1.5) | D (T3.2) | `tests/fixtures/mocks/` (T3.0) |
| `reports/drift/drift_summary.json` | C (T2.6) | D (T3.2, T3.4) | `tests/fixtures/mocks/` (T3.0) |
| `logs/alerts.jsonl` | D (T3.3) | D (T3.4) | — |

> `data/` e `models/` **não vão para o git**, e `logs/` só vai na execução final (T3.8).
> Todo o pipeline é reprodutível (seed fixa), então cada pessoa gera os artefatos reais
> localmente rodando os scripts (`prepare_data.py` → `train_baseline.py` → …).

## 1. Datasets (Parquet)

Colunas definidas em `src/credit_risk/config.py`:

| Arquivo | Colunas |
|---|---|
| `reference.parquet` | `ID_COLUMN` + `FEATURES` + `TARGET` |
| `production_base.parquet` | `ID_COLUMN` + `FEATURES` + `TARGET` |
| `<janela>.parquet` (`t1`…`tN`) | `ID_COLUMN` + `FEATURES` + `TARGET` (o target já reflete o concept drift) |
| `bad_batch.parquet` | mesmas colunas, com violações intencionais |

- `ID_COLUMN = "application_id"`: string única por proposta, criada em `prepare_data.py`.
  **Nunca** vai para o log em claro: é pseudonimizado (`privacy.pseudonymize_id`).
- Antes de predizer, `TARGET` é removido (o schema de inferência não tem target). O target
  das janelas só é usado para medir a performance (concept drift).

## 2. `logs/predictions.jsonl` (uma linha por predição)

```json
{"timestamp": "2026-11-01T12:00:00Z", "window": "t3", "record_id": "9f2c…",
 "score": 0.42, "decision": "denied", "latency_ms": 3.1, "model_version": "baseline_v1"}
```

| Campo | Tipo | Regra |
|---|---|---|
| `timestamp` | str ISO-8601 UTC | — |
| `window` | str | `t1`…`tN` |
| `record_id` | str | hash SHA-256 de `application_id` + salt |
| `score` | float \| null | probabilidade de default; `null` se a predição falhou |
| `decision` | str | `approved` (score < `APPROVAL_THRESHOLD`), `denied` ou `error` |
| `latency_ms` | float | tempo de predição do registro |
| `model_version` | str | `config.MODEL_VERSION` |

## 3. `logs/validation.jsonl` (uma linha por lote validado)

```json
{"timestamp": "2026-11-01T12:00:00Z", "batch_name": "t3", "rows": 5000,
 "status": "blocked", "n_failures": 12, "failed_rules": ["person_age_range", "no_duplicates"]}
```

`status` ∈ {`passed`, `blocked`}. Os nomes das regras em `failed_rules` são os nomes
dados aos checks no schema Pandera (T1.4).

## 4. `reports/drift/drift_summary.json`

```json
{
  "generated_at": "2026-11-01T12:00:00Z",
  "reference_rows": 19000,
  "windows": [
    {
      "window": "t3",
      "rows": 5000,
      "n_features": 11,
      "n_drifted": 2,
      "share_drifted": 0.18,
      "features": [
        {"feature": "person_income", "psi": 0.31, "ks_pvalue": 0.0001,
         "status": "drift", "drift_detected": true}
      ],
      "prediction_drift": {"psi": 0.12, "mean_score_ref": 0.21, "mean_score_cur": 0.27},
      "performance": {"auc": 0.81, "ks": 0.48},
      "report_html": "reports/drift/drift_t3.html"
    }
  ]
}
```

`psi` e `ks_pvalue` vêm do Evidently (método `psi` e `ks`). `status` ∈ {`stable`, `warning`, `drift`}, segundo
`PSI_WARNING`/`PSI_DRIFT`. `drift_detected` = PSI acima de `PSI_DRIFT` **ou** `ks_pvalue` < `KS_PVALUE`.
`performance` pode ser `null` se a janela não tiver target.

## 5. `logs/alerts.jsonl`

```json
{"timestamp": "2026-11-01T12:00:00Z", "window": "t3", "type": "data_drift",
 "metric": "share_drifted", "value": 0.36, "threshold": 0.30, "severity": "critical",
 "message": "36% das features com drift na janela t3"}
```

`type` ∈ {`data_drift`, `prediction_drift`, `performance_drop`, `null_predictions`,
`latency`, `contract_blocked`}. `severity` ∈ {`warning`, `critical`}.

## 6. `reports/training/metrics.json`

```json
{"model_version": "baseline_v1", "trained_at": "2026-10-25T12:00:00Z",
 "n_train": 15000, "n_valid": 4000, "auc": 0.90, "ks": 0.65, "gini": 0.80,
 "f1": 0.70, "precision": 0.75, "recall": 0.66, "threshold": 0.5}
```

`reports/training/feature_importance.csv`: colunas `feature,importance`, em ordem
decrescente.

## 7. Funções públicas

As assinaturas dos stubs em `src/credit_risk/` também são interface. Mudar nome,
parâmetros ou retorno de uma função usada por outra trilha segue a mesma regra de PR acima.

## Como não ficar travado

1. **Dados:** use `make_synthetic_credit_df(n, seed)` e `make_synthetic_window(...)` de
   `tests/fixtures/synthetic.py` (T0.5). Eles geram DataFrames com as mesmas colunas do
   dataset real, incluindo uma coluna `score` opcional.
2. **Arquivos de log/relatório:** use os exemplos em `tests/fixtures/mocks/` (T3.0), que
   seguem as seções 2–5.
3. **Função de outra trilha ainda não implementada:** escreva o seu código contra a
   assinatura e, no teste, use `monkeypatch` para substituir a função por um fake.
4. **Integração real:** acontece nos marcos semanais do `TODO.md`, e não "quando o
   colega terminar".
