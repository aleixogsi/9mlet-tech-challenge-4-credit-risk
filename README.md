# Credit Risk: Sustentação e Confiabilidade em Produção

> Tech Challenge Fase 4 (MLET / FIAP Pós Tech): observabilidade contínua, detecção de
> drift, qualidade de dados e governança (LGPD) de um modelo de Credit Scoring.

O projeto é desenvolvido em quatro etapas. O status das tarefas e os responsáveis estão
em [TODO.md](TODO.md).

## Contexto

Uma fintech de crédito tem um modelo de Credit Scoring em produção. Com mudanças na
economia (inflação, juros, novos perfis de clientes), há suspeita de **degradação
silenciosa**. Este projeto constrói a camada que:

1. **impede dados ruins de chegar ao modelo** (data contracts);
2. **detecta Data Drift e Concept Drift** (PSI, KS, Evidently);
3. **dá visibilidade operacional** (logs, métricas de saúde, alertas);
4. **documenta a governança** (LGPD, vieses, análise causal).

## Stack

| Função | Ferramenta |
|---|---|
| Modelo | scikit-learn + XGBoost |
| Data contracts | Pandera |
| Drift e relatórios | Evidently AI (testes PSI e KS) |
| Monitoramento | Relatórios Evidently + painel HTML |
| Ambiente | uv + pyproject.toml |

## Como rodar

```bash
uv sync
uv run pytest
```

O dataset bruto não é versionado. Para reproduzir a Etapa 1, faça o download pela fonte
Kaggle `laotse/credit-risk-dataset` e salve o arquivo como
`data/raw/credit_risk_dataset.csv`. Em seguida:

```bash
uv run python scripts/prepare_data.py
uv run python scripts/validate_data.py --make-bad-batch
uv run python scripts/train_baseline.py
```

## Dataset

O projeto usa o **Credit Risk Dataset**, disponibilizado publicamente no Kaggle por
`laotse/credit-risk-dataset`. O arquivo possui 32.581 registros antes da limpeza e as
colunas de idade, renda, emprego, empréstimo, taxa de juros, intenção, grau e histórico
de inadimplência. Após a limpeza e divisão determinística com seed 42, a base limpa
possui 28.634 registros, a Referência possui 17.180 registros e a Produção possui
11.454 registros.

O pipeline mantém a Referência e a Produção em arquivos físicos separados. O modelo
nunca é treinado com a Produção.

## Etapa 1: Validação de dados (data contracts)

O contrato Pandera bloqueia a ingestão quando ocorre qualquer violação. As regras rígidas
incluem idade entre 18 e 100 anos, renda não nula e dentro dos limites definidos,
ausência de duplicatas, target binário e domínios válidos para variáveis categóricas.

O lote inválido é gerado por `scripts/validate_data.py --make-bad-batch`, que retorna
exit code 1, registra a falha em `logs/validation.jsonl` e gera a evidência em
`reports/validation/bad_batch_failures.csv`.

O baseline XGBoost é treinado exclusivamente com a Referência. As métricas estão em
`reports/training/metrics.json` e as importâncias em
`reports/training/feature_importance.csv`.

## Etapa 2: Simulação e detecção de drift

Em desenvolvimento. Consulte [TODO.md](TODO.md) para o status da Etapa 2.

## Etapa 3: Observabilidade e monitoramento

TODO(T3.6): métricas de saúde escolhidas, alertas e link para `reports/monitoring/index.html`.

## Etapa 4: Governança e LGPD

### Tratamento de dados pessoais (PII)
TODO(T4.1)

### Base legal da decisão de crédito
TODO(T4.2)

### Plano de retenção
TODO(T4.2)

### Mitigação de vieses
TODO(T4.3): resultados de `reports/training/fairness.csv`

### Análise causal da degradação
TODO(T4.4)

## Vídeo STAR

TODO(T4.7): link do vídeo (≤ 5 min).

## Equipe

TODO: nomes e RMs dos 4 integrantes.
