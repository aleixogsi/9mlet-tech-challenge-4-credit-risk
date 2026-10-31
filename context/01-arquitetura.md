# Arquitetura e decisões técnicas

> Proposta de arquitetura **derivada** de [00-tech-challenge.md](00-tech-challenge.md).
> Diferente do enunciado, este arquivo **pode e deve evoluir**. Toda decisão nova vai
> para a tabela "Registro de decisões" no fim do arquivo.

## Visão geral do pipeline

```
 dados brutos ──► split temporal/aleatório ──► REFERÊNCIA ──► contrato (Pandera/GX) ──► treino baseline ──► modelo
                                     │
                                     └──► base de PRODUÇÃO ──► simulação de drift (janelas t1..tN)
                                                                   │
                       lote com erros ──► contrato ──► ❌ BLOQUEADO (log + relatório de falha)
                                                                   │
                                          contrato ✅ ──► predição ──► log de predições (JSONL/Parquet)
                                                                   │
                               Evidently (Referência × Produção): Data Drift, Prediction Drift,
                               Classification/Concept Drift ──► relatórios HTML + métricas JSON
                                                                   │
                               Monitoramento: métricas de saúde + alertas ──► relatórios/dashboard
```

## Estrutura de pastas

```
.
├── CLAUDE.md · .claude/           # contexto e configuração do Claude Code
├── .github/                       # contexto do Copilot (instructions/, prompts/)
├── .vscode/                       # settings compartilhados do VS Code
├── context/                       # EXCLUSIVO: contexto compartilhado pelas IAs (Claude + Copilot)
├── README.md                      # ENTREGA: como rodar, evidências, Governança/LGPD, causalidade, vídeo
├── TODO.md                        # backlog e divisão de tarefas da equipe (IDs T0.1…T4.8)
├── pyproject.toml · uv.lock       # dependências (uv) + config de ruff/pytest
├── .env.example                   # variáveis necessárias (.env real nunca versionado)
├── configs/
│   └── drift_scenarios.yaml       # janelas t1..tN: feature, operação, tipo, justificativa econômica
├── data/                          # NÃO versionado
│   ├── raw/                       # dataset original
│   ├── reference/                 # REFERÊNCIA (treino)
│   ├── production/                # PRODUÇÃO: base + janelas com drift
│   └── bad_batches/               # lote com erros (demo do contrato bloqueando)
├── src/credit_risk/
│   ├── config.py                  # caminhos, seed, colunas, limites do contrato, thresholds
│   ├── data/                      # load, clean, split (Ref × Prod), privacy (LGPD)
│   ├── contracts/                 # schemas (Pandera), validator (bloqueante), bad_batch
│   ├── training/                  # pipeline, train, evaluate (AUC/KS/Gini, importance), fairness
│   ├── drift/                     # scenarios (data + concept), reports (Evidently, com PSI/KS)
│   └── monitoring/                # prediction_logger, health, alerts, dashboard
├── scripts/                       # entrypoints CLI (ver abaixo)
├── models/                        # baseline_v1.joblib (não versionado)
├── reports/                       # VERSIONADO (entregável)
│   ├── validation/                # evidência do lote bloqueado
│   ├── training/                  # metrics.json, feature importance, model card
│   ├── drift/                     # drift_<janela>.html, performance_<janela>.html, psi_ks_<janela>.csv
│   └── monitoring/                # index.html (painel de saúde e alertas)
├── logs/                          # predictions.jsonl, validation.jsonl, alerts.jsonl (VERSIONADO só na execução final, T3.8)
├── tests/                         # pytest (smoke, contracts, drift, monitoring)
└── docs/                          # documentação do projeto (NÃO é contexto de IA; o enunciado não exige)
```

Cada função ainda não implementada lança `NotImplementedError("<ID>")`, com o ID da
tarefa correspondente em `TODO.md`.

## Entrypoints esperados (um por etapa)

| Script | Etapa | Faz |
|---|---|---|
| `scripts/prepare_data.py` | 1 | Baixa/carrega os dados, limpa e separa Referência × Produção |
| `scripts/validate_data.py` | 1 | Roda o contrato num dataset/lote e sai com **exit code ≠ 0** se falhar |
| `scripts/train_baseline.py` | 1 | Treina e avalia o baseline (AUC, KS, Gini, F1) e salva o modelo |
| `scripts/simulate_drift.py` | 2 | Gera as janelas de produção com drift controlado e reprodutível (seed) |
| `scripts/predict.py` | 2/3 | Valida pelo contrato, prediz e grava o log de predições |
| `scripts/detect_drift.py` | 2 | Gera os relatórios Evidently (HTML + JSON) e a tabela PSI/KS por feature |
| `scripts/bias_report.py` | 4 | Gera `reports/training/fairness.csv` (evidência da seção de vieses) |
| `scripts/monitor.py` | 3 | Consolida métricas de saúde e alertas e gera relatório/dashboard |
| `scripts/run_pipeline.py` | todas | Executa tudo de ponta a ponta (demo do vídeo) |

## Decisões de design obrigatórias (vêm do enunciado)

1. **Referência × Produção separados fisicamente** (pastas/arquivos distintos) e nunca
   misturados no treino.
2. **Contrato bloqueante:** dados inválidos não chegam ao modelo. A validação levanta
   exceção ou retorna exit code ≠ 0, e a falha é logada e reportada.
3. **No mínimo 3 regras rígidas** no contrato. Sugestões alinhadas ao enunciado:
   - idade ≥ 18 (e teto plausível, ex.: ≤ 100);
   - renda não nula e > 0, dentro de limites plausíveis;
   - sem duplicatas (por ID ou pela linha inteira);
   - target binário {0, 1} (no dataset de treino);
   - tipos e domínios de categóricas válidos.
4. **Drift em pelo menos 2 features importantes**, de preferência as de maior
   importância no modelo (ex.: renda, desemprego/tempo de emprego, dívida/renda, taxa
   de juros).
5. **Data Drift e Concept Drift:**
   - *Data drift*: mudança em P(X), ex.: deslocar a média ou escalar a renda (inflação).
   - *Concept drift*: mudança em P(y|X), ex.: o mesmo perfil passa a ter mais default
     (rotular de novo parte da produção segundo uma regra econômica documentada). Isso
     aparece como queda de performance com o rótulo real chegando depois.
6. **Testes estatísticos explícitos:** PSI e KS por feature, **calculados pelo Evidently**
   (método de drift configurado como `psi` e `ks`, sem reimplementação), com thresholds no `config.py`
   (referência de mercado para PSI: < 0,1 estável; 0,1–0,25 atenção; > 0,25 drift).
7. **Reprodutibilidade:** seeds fixas e parâmetros da simulação versionados.
8. **Relatórios HTML versionados em `reports/`**, porque são entregáveis do repositório.

## Métricas de saúde (Etapa 3)

Mínimo a documentar e exibir:

- **Volume** de predições por janela;
- **% de predições nulas/erro** e **% de lotes bloqueados** pelo contrato;
- **Latência** de predição (p50/p95);
- **Distribuição do score** e taxa de aprovação por janela (prediction drift);
- **Nº de features com drift** e **share de features com drift** por janela;
- **Performance** (AUC/KS/Gini) quando houver rótulo, para evidenciar o concept drift;
- **Alertas** disparados (tipo, janela, feature, valor, threshold).

## Registro de decisões

| # | Decisão | Escolha | Motivo |
|---|---|---|---|
| D1 | Dataset | **Credit Risk Dataset (Kaggle, ~32 mil linhas)**. Alternativa: Give Me Some Credit | ≥ 5.000 amostras; tem idade, renda, tempo de emprego e taxa de juros (encaixa nos exemplos do enunciado e na história de inflação/juros) |
| D2 | Lib de contratos | **Pandera** | Mais simples e pythônico que o GX, integra direto ao pandas |
| D3 | Observabilidade | **Evidently + painel HTML simples** (métricas de saúde, alertas e links). Prometheus + Grafana só como extra | Cobre a Etapa 3 sem depender de infraestrutura |
| D6 | Escopo enxuto | Sem notebooks, sem PSI/KS próprios, sem `infra/` | O enunciado não exige; o foco vai para o que tem peso na nota |
| D7 | Evidências para o avaliador | Logs e relatórios da execução final versionados; dataset bruto versionado se a licença permitir | O avaliador precisa ver os logs e conseguir rodar sem conta no Kaggle |
| D4 | Modelo | **XGBoost** (Regressão Logística opcional para comparação) | Feature importance orienta a escolha das features com drift |
| D5 | Gerenciador de ambiente | **uv + pyproject.toml** (versões travadas em `uv.lock`) | Reprodutível e rápido; a API do Evidently muda entre versões |
