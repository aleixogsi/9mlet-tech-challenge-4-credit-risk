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
├── apresentacao/demo/             # página de demonstração do vídeo (VERSIONADA, D19); o resto de apresentacao/ é local (D14)
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
| D7 | Evidências para o avaliador | Logs e relatórios da execução final versionados; **CSV bruto versionado** (licença CC0 confirmada no Kaggle em 15/11/2026) | O avaliador precisa ver os logs e conseguir rodar sem conta no Kaggle |
| D4 | Modelo | **XGBoost** (Regressão Logística opcional para comparação) | Feature importance orienta a escolha das features com drift |
| D5 | Gerenciador de ambiente | **uv + pyproject.toml** (versões travadas em `uv.lock`) | Reprodutível e rápido; a API do Evidently muda entre versões |
| D8 | Base e grupos do relatório de vieses | Holdout de 20% da Referência (mesmo split do baseline, `split_reference`); faixa etária e `person_home_ownership`; alerta pela regra dos 4/5 (razão < 0,8) em grupos com ≥ 30 propostas; grupos menores saem só com o volume (taxas suprimidas) | Mede o modelo em dados que ele não viu, com a mesma base das métricas do baseline |
| D9 | `person_age` no modelo | **Mantida** como feature, com medição de viés a cada execução | Retirá-la refaria as evidências das Etapas 1 a 3; a importância é de 1,5%; no holdout nenhuma faixa ficou abaixo de 0,97, e na crise (t5) a menor razão é 0,88 (18–25 anos) |
| D10 | `loan_intent = MEDICAL` | Mantido como categoria, tratado como potencialmente sensível; só agregados | É a finalidade do empréstimo, não um diagnóstico; se o DPO discordar, generalizar ou remover e retreinar |
| D11 | Integração antes da Etapa 4 | Etapa 4 desenvolvida em `feat/etapa4-governanca` a partir da Etapa 3 | Evita a Etapa 4 nascer de uma branch não revisada |
| D12 | Apresentação do vídeo | Vitor apresenta; terminal e Evidently mostrados com comandos já executados | Dono da Etapa 4; o pipeline completo é lento demais para gravar ao vivo |
| D13 | Profundidade da análise causal | Só documentação, com os números existentes (t1→t3 só data drift; t3→t5 com concept drift), mais um contrafactual reproduzível no README (mesmas janelas sem concept drift) para separar os dois efeitos | O enunciado pede documentação, e a simulação controlada já separa causa e efeito |
| D14 | Material de apresentação | Deck STAR e página de demonstração locais (`apresentacao/`, fora do Git) | Apoiam o vídeo sem virar entregável; o visual da página foi aprovado em 15/11/2026 |
| D15 | ID nos relatórios de falha do contrato | `write_validation_report` pseudonimiza a coluna de ID (SHA-256 com salt) | O relatório é versionado, e o ID nunca aparece em claro (05-interfaces) |
| D16 | Prints do roteiro do vídeo | Prints anotados (onde clicar e apontar) versionados em `docs/roteiro-video/` (JPEG); o gerador fica em `apresentacao/roteiro/` (local) | O roteiro é versionado e precisa das imagens; os prints só têm agregados e IDs com hash |
| D17 | Celular ao vivo na página de demonstração | Com o `serve.py`, "Atualizar dados" sorteia um cliente da base de produção com o drift da janela aplicado na hora (mesmo YAML), e "Pedir análise" passa pelo contrato e pelo modelo. Cena 1: janela t1. Cena 4: degradação silenciosa forçada (bom pagador de t5 na regra do concept drift, aprovado com score < 0,2). Sorteio sem seed só na demo; MEDICAL fica fora (D10); nada vai para `logs/` | Pedido do Vitor (15/11/2026): cada teste no vídeo é real e diferente, e as cenas 2, 3 e 5 continuam mostrando a evidência versionada |
| D18 | Contrato rodado de dentro da página de demonstração | Na cena 1, o botão "Testar lote com erro" chama o `serve.py`, que roda `scripts/validate_data.py --make-bad-batch` e devolve a saída real, o exit code e o tempo para um terminal desenhado na página. O terminal fica na tela e a troca de cena é manual, pelo botão "Próxima etapa" da barra superior, que só libera depois da ação ao vivo da cena (cena 1: o teste do lote; cena 4: o aviso de inadimplência no celular). O `serve.py` devolve `logs/validation.jsonl` e `reports/validation/` ao conteúdo de antes. Sem o servidor, a página repete a saída do log ("replay do log") | Pedido do Vitor (15/11/2026): no A2 do vídeo, trocar para o PowerShell e voltar gastava tempo; o comando e o bloqueio continuam reais. A troca manual de cena veio depois, também a pedido dele: o avanço automático não dava tempo de mostrar o terminal |
| D19 | Página de demonstração no repositório | `apresentacao/demo/` passa a ser versionada (`index.html`, `styles.css`, `data.js`, `build_data.py`, `serve.py`), sem os prints de `shots/`. O deck e a edição do vídeo continuam locais (D14). `tests/test_demo_page.py` confere que o `data.js` bate com `logs/` e `reports/` e que nenhum ID completo aparece na página | O vídeo apresenta a página como o painel de observabilidade, e o roteiro versionado já mandava rodar `apresentacao/demo/serve.py`. Fora do Git, o avaliador não conseguia conferir. Pedido do Vitor (15/11/2026) |
