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

### Pré-requisitos

- Python 3.11 ou superior;
- `uv` instalado;
- acesso à internet para o download pelo KaggleHub.

O KaggleHub utiliza a sessão autenticada disponível no ambiente. Se o Kaggle solicitar
autenticação, configure-a localmente conforme a documentação do KaggleHub. Credenciais
e arquivos `.env` nunca devem ser adicionados ao repositório.

### Execução completa da Etapa 1

```bash
uv sync
uv run python scripts/download_data.py
uv run python scripts/prepare_data.py
uv run python scripts/validate_data.py --make-bad-batch
uv run python scripts/train_baseline.py
uv run pytest
```

O fluxo executa as seguintes operações:

1. `download_data.py` baixa o dataset público `laotse/credit-risk-dataset`, valida as
   colunas obrigatórias e salva o CSV em `data/raw/credit_risk_dataset.csv`;
2. `prepare_data.py` remove registros inválidos, cria identificadores internos e separa
   Referência e Produção em arquivos Parquet distintos;
3. `validate_data.py --make-bad-batch` gera um lote com violações intencionais, executa o
   contrato Pandera e demonstra o bloqueio com exit code `1`;
4. `train_baseline.py` valida a Referência, treina o XGBoost e salva as métricas e
   importâncias das features.

Para validar um lote já existente:

```bash
uv run python scripts/validate_data.py data/reference/reference.parquet --schema training
uv run python scripts/validate_data.py data/bad_batches/bad_batch.parquet --schema training
```

O segundo comando deve falhar com exit code `1`.

### Execução sem download automático

Se o ambiente não permitir o download pelo KaggleHub, baixe manualmente o arquivo
`credit_risk_dataset.csv` pela mesma fonte e salve-o em `data/raw/`. A partir daí, execute
os scripts de preparação, validação e treinamento normalmente.

### Artefatos gerados

| Caminho | Finalidade |
|---|---|
| `data/reference/reference.parquet` | Base de Referência usada no treino |
| `data/production/production_base.parquet` | Base de Produção separada |
| `data/bad_batches/bad_batch.parquet` | Lote inválido para demonstração |
| `reports/validation/bad_batch_failures.csv` | Evidência das regras violadas |
| `reports/training/metrics.json` | Métricas do baseline |
| `reports/training/feature_importance.csv` | Importância das features |
| `models/baseline_v1.joblib` | Modelo treinado localmente |

Datasets, modelos e logs locais não são versionados. Os relatórios pequenos e
reprodutíveis são versionados como evidência da execução.

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

### Execução

```bash
uv run python scripts/simulate_drift.py   # gera data/production/t1..t5.parquet
uv run python scripts/predict.py          # valida pelo contrato, prediz e grava logs/predictions.jsonl
uv run python scripts/detect_drift.py     # relatórios Evidently em reports/drift/
uv run pytest tests/test_drift.py tests/test_drift_pipeline.py tests/test_inference.py
```

Os scripts aceitam `--window t3` (predição e detecção) para processar só uma janela.
Defina `PSEUDONYMIZATION_SALT` no `.env` para que o `record_id` do log seja estável entre
execuções; sem ele, o script usa um salt aleatório por execução e o log continua sem PII.

### Simulação da passagem do tempo

`configs/drift_scenarios.yaml` descreve cinco janelas de produção com 5.000 propostas
cada, amostradas da base de Produção (nunca da Referência) com seed fixa. Cada mudança
tem uma justificativa econômica, que alimenta a análise causal da Etapa 4.

| Janela | Cenário | Data drift (P(X)) | Concept drift (P(y\|X)) |
|---|---|---|---|
| t1 | Controle | nenhum | nenhum |
| t2 | Início da inflação | renda ×1,10; juros +0,75 p.p. | nenhum |
| t3 | Inflação + juros | renda ×1,20; juros +2,5 p.p.; parcela/renda +0,03 | nenhum |
| t4 | Desaceleração | renda ×1,25; juros +4 p.p.; parcela/renda +0,06; tempo de emprego ×0,6 | 15% dos bons pagadores com parcela/renda > 0,25 passam a inadimplir |
| t5 | Crise | renda ×1,30; juros +5 p.p.; parcela/renda +0,08; tempo de emprego ×0,5 | 30% dos bons pagadores com parcela/renda > 0,25 passam a inadimplir |

As features alteradas foram escolhidas pela importância do baseline
(`reports/training/feature_importance.csv`): `loan_percent_income` e `loan_int_rate`
são as duas features numéricas mais importantes do modelo, e `person_income` e
`person_emp_length` completam o cenário de inflação e desemprego.

### Detecção

`scripts/detect_drift.py` compara a Referência com cada janela usando o **Evidently AI**:

- **PSI** por feature (`method="psi"`), classificado em `stable` (< 0,10), `warning`
  (0,10–0,25) e `drift` (> 0,25);
- **Kolmogorov-Smirnov** por feature numérica (`method="ks"`, drift se p-valor < 0,05);
- **prediction drift**: PSI do score do modelo;
- **performance** com o rótulo real (`ClassificationPreset`), para evidenciar o concept
  drift.

Uma feature é marcada com drift quando o PSI passa de 0,25 **ou** o p-valor do KS fica
abaixo de 0,05. O veredito de dataset drift do HTML usa o mesmo limiar dos alertas
(30% das features).

### Resultados

| Janela | Features com drift | Quais | PSI do score | Score médio | AUC | KS |
|---|---|---|---|---|---|---|
| t1 | 2/11 (18%) | `person_age`, `person_emp_length` | 0,004 | 0,214 | 0,924 | 0,711 |
| t2 | 2/11 (18%) | `person_income`, `loan_int_rate` | 0,022 | 0,224 | 0,914 | 0,691 |
| t3 | 3/11 (27%) | `person_income`, `loan_int_rate`, `loan_percent_income` | 0,224 | 0,288 | 0,891 | 0,647 |
| t4 | 4/11 (36%) | `person_income`, `person_emp_length`, `loan_int_rate`, `loan_percent_income` | 0,625 | 0,390 | 0,842 | 0,567 |
| t5 | 4/11 (36%) | `person_income`, `person_emp_length`, `loan_int_rate`, `loan_percent_income` | 0,830 | 0,444 | 0,801 | 0,480 |

Na Referência, o score médio é 0,217 e a AUC é 0,942.

Leitura dos resultados:

- o drift cresce de t2 a t5 e atinge exatamente as features alteradas na simulação;
- `person_income` é detectada pelo KS (p-valor ≈ 0), mas o PSI dela fica em 0,07 mesmo
  em t5: o PSI, calculado por faixas, foi pouco sensível a esse deslocamento, enquanto o
  KS compara a distribuição acumulada inteira. Por isso o projeto usa os dois testes;
- a AUC já cai com o data drift (0,924 em t1 para 0,891 em t3) e cai mais com o concept
  drift de t4 e t5, que muda só o rótulo e não as features: 0,801 em t5. O score médio
  dobra em relação à Referência;
- na janela de controle t1, o KS marca `person_age` e `person_emp_length` com p-valor
  ≈ 0,035, enquanto o PSI de todas as features fica abaixo de 0,02. Com amostras grandes,
  o KS detecta diferenças pequenas de amostragem. Isso não chega ao limiar de 30% e
  mostra por que o alerta considera a proporção de features e não uma feature isolada.

### Evidências

| Caminho | Conteúdo |
|---|---|
| `reports/drift/drift_<janela>.html` | Relatório Evidently de data drift e prediction drift |
| `reports/drift/performance_<janela>.html` | Relatório Evidently de performance (concept drift) |
| `reports/drift/psi_ks_<janela>.csv` | PSI, p-valor do KS e status por feature |
| `reports/drift/drift_summary.json` | Resumo consumido pelo monitoramento (Etapa 3) |
| `logs/predictions.jsonl` | Log de predições sem PII (versionado só na execução final, T3.8) |

## Etapa 3: Observabilidade e monitoramento

A camada de observabilidade integra os logs operacionais de validação (`logs/validation.jsonl`) e de inferência sem PII (`logs/predictions.jsonl`) aos resultados estatísticos de drift (`reports/drift/drift_summary.json`).

### Testes de observabilidade e mocks (`T3.0`)

Para permitir testes unitários rápidos e desacoplados da execução completa do pipeline, `tests/fixtures/mocks/` disponibiliza arquivos sintéticos que seguem estritamente os contratos de interface do projeto (`predictions.jsonl`, `validation.jsonl` e `drift_summary.json`):

```bash
uv run pytest tests/test_monitoring.py
```

### Registro centralizado de predições sem PII (`T3.1`)

O módulo `src/credit_risk/monitoring/prediction_logger.py` implementa `log_predictions` e `read_predictions`, garantindo que cada linha gravada em `logs/predictions.jsonl` contenha exclusivamente os campos autorizados (`timestamp`, `window`, `record_id`, `score`, `decision`, `latency_ms`, `model_version`) e que `record_id` seja obrigatoriamente um hash SHA-256 hexadecimal de 64 caracteres (bloqueando qualquer tentativa de gravar identificadores originais ou PII).

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
