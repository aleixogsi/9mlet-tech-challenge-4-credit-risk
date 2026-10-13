# Credit Risk: Sustentação e Confiabilidade em Produção

> Tech Challenge Fase 4 (MLET / FIAP Pós Tech): observabilidade contínua, detecção de
> drift, qualidade de dados e governança (LGPD) de um modelo de Credit Scoring.

🚧 **Em construção.** Divisão de tarefas em [TODO.md](TODO.md). As seções marcadas com
`TODO` serão preenchidas ao longo do desenvolvimento.

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
uv sync                                  # instala as dependências
uv run python scripts/run_pipeline.py    # executa tudo de ponta a ponta
uv run pytest                            # testes
```

TODO(T4.5): instruções para baixar o dataset e descrição de cada script.

## Dataset

TODO(T0.2): Credit Risk Dataset (Kaggle): origem, licença, nº de linhas, dicionário de
variáveis e separação Referência × Produção.

## Etapa 1: Validação de dados (data contracts)

TODO(T4.5): regras do contrato, evidência do lote bloqueado (`reports/validation/`) e
métricas do baseline (`reports/training/`).

## Etapa 2: Simulação e detecção de drift

TODO(T4.5): cenários (`configs/drift_scenarios.yaml`), tabela PSI/KS e links para os
relatórios do Evidently (`reports/drift/`).

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
