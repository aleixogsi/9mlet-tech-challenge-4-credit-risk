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
