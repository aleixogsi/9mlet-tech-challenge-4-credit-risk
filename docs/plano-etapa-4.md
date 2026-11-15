# Plano de desenvolvimento da Etapa 4: Governança e vídeo STAR

> Responsável: Vitor (ver [TODO.md](../TODO.md)). Base: enunciado oficial (PDF, p. 5–6) e
> estado da branch `feat/step-3` em 15/11/2026.
>
> ⏰ **Entrega: 17/11/2026** (prazo registrado em outubro; confirmar com o grupo). Restam
> 2 dias. A prioridade segue o peso na nota: Governança (15%) e Vídeo (15%). Itens que não
> pontuam (CI, extras) só entram se sobrar tempo. Ver o cronograma na seção 7.

## 1. O que o enunciado exige

**Etapa 4: Governança (Privacy by Design e by Default).** Foco: documentação
arquitetural, compliance e prescrição.

| Exigência do enunciado | Onde precisa estar |
|---|---|
| Plano de proteção de dados: como a **PII** foi tratada | `README.md` |
| **Base legal** da decisão de crédito | `README.md` |
| **Plano de retenção** | `README.md` |
| **Causalidade** (análise causal do problema) | `README.md` |
| **Mitigação de vieses** (aparece no critério de 15%) | `README.md` |
| Vídeo STAR de até 5 min, com **link no README** | YouTube + `README.md` |
| "Documentação consolidada de Governança no README" | requisito do repositório |

O que conta na nota:

- **Governança (LGPD), 15%:** clareza sobre privacidade, base legal e **mitigação de vieses**.
- **Vídeo STAR, 15%:** clareza na demonstração técnica da degradação do modelo e
  explicação do impacto (≤ 5 min). **Regra do grupo: menos de 4:59.**

O que o vídeo precisa cobrir em cada parte (texto do enunciado):

| Parte | Conteúdo obrigatório |
|---|---|
| **S**ituation | o risco da degradação silenciosa de modelos de crédito no mundo real |
| **T**ask | interceptar dados ruins, detectar drift, garantir compliance |
| **A**ction | ferramentas de validação e observabilidade, simulação do drift e plano de governança |
| **R**esult | demonstração do relatório apontando o drift, alertas gerados e **lições aprendidas** |

## 2. Diagnóstico: o que já existe e o que falta

### Já pronto (Etapas 1–3), que a Etapa 4 vai citar como evidência

| Item | Evidência |
|---|---|
| Minimização de colunas | `src/credit_risk/data/privacy.py::minimize_columns`, usado em `prepare_data.py` |
| Pseudonimização (SHA-256 + salt) | `privacy.py::pseudonymize_id`; salt em `.env` (`PSEUDONYMIZATION_SALT`) |
| Log de predições só com campos permitidos | `monitoring/prediction_logger.py` (rejeita `record_id` que não seja hash) |
| ID interno sem dado pessoal | `data/load.py` cria `application_<n>` |
| Dados e modelo fora do Git | `.gitignore` (`data/**`, `models/*.joblib`) |
| Justificativa econômica de cada mudança | `configs/drift_scenarios.yaml` (campo `rationale`), base da análise causal |
| Números de drift e performance por janela | `reports/drift/drift_summary.json` e tabela no README |
| Alertas | `logs/alerts.jsonl` e `reports/monitoring/index.html` |

### Falta (escopo da Etapa 4)

| ID | Tarefa | Situação atual |
|---|---|---|
| T4.1 | Tratamento de PII no README | `TODO(T4.1)` no README |
| T4.2 | Base legal e retenção no README | `TODO(T4.2)` no README |
| T4.3 | Relatório de vieses + mitigação | `fairness.py` e `bias_report.py` lançam `NotImplementedError` |
| T4.4 | Análise causal no README | `TODO(T4.4)` no README |
| T4.5 | Como executar + mapa de evidências | README organizado por etapa, sem um "começo rápido" único |
| T4.6 | Roteiro do vídeo | não existe |
| T4.7 | Gravar o vídeo e pôr o link | `TODO(T4.7)` no README |
| T4.8 | Revisão final | — |
| T0.6 | CI com testes em cada PR | não há `.github/workflows/` |

### Problemas encontrados na leitura

1. **O pipeline ponta a ponta está quebrado.** `scripts/run_pipeline.py` chama
   `bias_report.py`, que ainda lança `NotImplementedError("T4.3")`. A T4.3 resolve isso e
   precisa vir primeiro, porque a demo do vídeo depende do pipeline.
2. **Inconsistência no README:** a seção da Etapa 3 fala em "12 violações" do
   `bad_batch`, mas `logs/validation.jsonl` e `logs/alerts.jsonl` registram **8**.
3. **`ruff format --check` falha** em 2 arquivos (ex.: `contracts/schemas.py`). Um CI com
   checagem de formato quebraria no primeiro PR.
4. **`reports/validation/bad_batch_failures.csv` traz `application_id` em claro.** É um ID
   sintético (`application_00009043`), mas a regra de `05-interfaces.md` diz que o ID
   nunca aparece em claro. Decidir na auditoria da T4.1: pseudonimizar ou justificar.
5. **`loan_intent = MEDICAL`** pode revelar informação de saúde, que é **dado sensível**
   (LGPD, art. 5º, II). Vale tratar explicitamente no inventário de PII.
6. **`person_age` é feature do modelo** (1,4% da importância). Idade é atributo com risco
   de discriminação, então precisa de medição de viés e justificativa.
7. **`feat/step-2` e `feat/step-3` ainda não estão na `main`.** Só a Etapa 1 foi
   integrada.
8. **Não há dados nem modelo locais nesta máquina** (`data/` e `models/` vazios). Gerar o
   `fairness.csv` exige rodar `download_data.py` (sessão Kaggle) → `prepare_data.py` →
   `train_baseline.py`.

## 3. Pré-requisitos (antes de começar)

1. **Integrar as Etapas 2 e 3 na `main`** com um PR `feat/step-3 → main`. A step-3 já
   contém a step-2, então um PR basta. Se o grupo preferir, abre os dois em sequência.
2. **Criar a branch da Etapa 4** a partir da `main` atualizada (ou da `feat/step-3`, se o
   PR demorar): `feat/etapa4-governanca`.
3. **Gerar os artefatos locais:** `download_data.py`, `prepare_data.py`,
   `train_baseline.py`. A seed é fixa, então o modelo sai igual ao dos colegas.
4. **Fixar `PSEUDONYMIZATION_SALT` no `.env`**, para que a execução final gere `record_id`
   estáveis.

## 4. Frentes de trabalho

A única frente com código é a W1. As outras são documentação, CI e vídeo.

### W1. Relatório de vieses (T4.3), o único código da etapa

**Arquivos**

| Arquivo | Mudança |
|---|---|
| `src/credit_risk/config.py` | `AGE_BANDS` (ex.: 18–25, 26–35, 36–45, 46–60, 60+) e `FAIRNESS_MIN_RATIO = 0.8` |
| `src/credit_risk/training/fairness.py` | implementar `fairness_by_group` (mantendo a assinatura) |
| `scripts/bias_report.py` | carregar modelo + Referência, recriar o holdout de validação e gravar `reports/training/fairness.csv` |
| `tests/test_fairness.py` | testes com `make_synthetic_credit_df` e um modelo fake (`monkeypatch`) |

**Como calcular**

- **Base de avaliação:** o mesmo holdout de 20% da Referência usado em
  `train_baseline.py` (`train_test_split(test_size=0.2, random_state=SEED, stratify=TARGET)`).
  Avaliar no conjunto de treino daria números otimistas. Para não duplicar a regra, criar
  uma função de split compartilhada usada pelos dois scripts.
- **Grupos:** faixa etária (derivada de `person_age`) e `person_home_ownership`.
- **Colunas do CSV:** `group_col`, `group`, `n`, `approval_rate`, `default_rate`,
  `predicted_default_rate`, `auc`, `fnr` (inadimplente aprovado), `fpr` (bom pagador
  negado, que é o dano ao cliente), `approval_ratio` (aprovação do grupo ÷ maior taxa de
  aprovação) e `flag_disparity` (`approval_ratio < 0.8`, a "regra dos 4/5").
- **Grupos pequenos:** se `n` for baixo ou o grupo tiver uma única classe, AUC = `null`.
- **Opcional (forte para o vídeo):** `fairness_windows.csv` com a aprovação por faixa
  etária em t1…t5, para mostrar se a crise afeta mais um grupo do que outro.

**Testes mínimos:** colunas e tipos do CSV; um grupo com aprovação menor é marcado com
`flag_disparity`; grupo com uma única classe não quebra o cálculo; nenhuma coluna de ID no
resultado.

**Pronto quando:** `uv run python scripts/run_pipeline.py` roda do início ao fim e
`reports/training/fairness.csv` está versionado.

**Commits sugeridos**

- `feat(governance): implementa métricas de fairness por grupo`
- `feat(governance): gera relatório de vieses no pipeline`
- `test(governance): cobre métricas de fairness com dados sintéticos`

### W2. Privacidade, base legal e retenção no README (T4.1, T4.2)

Roteiro: [context/04-governanca-lgpd.md](../context/04-governanca-lgpd.md).

**Tratamento de PII (T4.1)**

- **Inventário de colunas** em tabela: identificador direto (nenhum no dataset público),
  quasi-identificadores (`person_age`, `person_income`, `person_emp_length`,
  `person_home_ownership`), dados de crédito (`cb_person_default_on_file`,
  `cb_person_cred_hist_length`, `loan_*`) e possível dado sensível (`loan_intent = MEDICAL`).
- **Controles aplicados, com link para o código:** minimização, ID sintético,
  pseudonimização com salt, log com campos permitidos, dados fora do Git, relatórios só com
  agregados.
- **Auditoria dos artefatos versionados:** `logs/`, `reports/` (resolver o item 4 da
  seção 2).
- **Privacy by Design e by Default:** mapear os princípios para o que o pipeline faz por
  padrão.

**Base legal (T4.2)**

- LGPD art. 7º, X (proteção do crédito) como base principal. Art. 7º, V (procedimentos
  preliminares de contrato) como complementar.
- Art. 20: direito à revisão de decisão automatizada e à explicação dos critérios. Ligar
  à `feature_importance.csv`.
- Art. 6º (finalidade, necessidade, **não discriminação**) e art. 46 (segurança).
- Lei 12.414/2011 (Cadastro Positivo), quando aplicável.
- Papéis de governança (dono do modelo, engenharia de ML, DPO, risco/compliance).

**Retenção (T4.2):** tabela por tipo de dado.

| Dado | Prazo sugerido | Justificativa | Ao fim do prazo |
|---|---|---|---|
| Dados de treino (Referência) | vida do modelo + período de auditoria | reprodutibilidade e auditoria | eliminar ou anonimizar |
| Base e janelas de produção | período de monitoramento | detecção de drift | eliminar |
| Logs de predição (pseudonimizados) | prazo regulatório definido pelo DPO | revisão de decisão (art. 20) e auditoria | eliminar |
| Relatórios agregados (sem PII) | indeterminado | histórico de monitoramento | manter |

> ⚠️ Os prazos legais citados (ex.: CDC art. 43, §1º; Lei 12.414/2011, art. 14; Lei
> 9.613/1998, art. 10) precisam ser **conferidos na fonte** antes de entrar no README.

**Commits sugeridos**

- `docs(governance): documenta tratamento de pii e privacy by design`
- `docs(governance): adiciona base legal e plano de retenção lgpd`

### W3. Vieses e análise causal no README (T4.3 doc, T4.4)

**Mitigação de vieses:** tabela resumida do `fairness.csv`, leitura dos grupos marcados e
medidas tomadas e propostas:

- atributos sensíveis fora do modelo;
- idade mantida com justificativa ou removida (ver decisão D9);
- monitorar o viés junto com o drift;
- revisão humana de casos limítrofes (art. 20).

**Análise causal (T4.4)**

1. **Diagrama causal (Mermaid, que o GitHub renderiza):**
   - inflação → renda nominal ↑ (`person_income`);
   - alta da Selic → `loan_int_rate` ↑;
   - perda de poder de compra → `loan_percent_income` ↑;
   - desemprego ↑ → `person_emp_length` ↓;
   - parcela alta + choque → default ↑ (concept drift).
2. **Causa → efeito observado,** com os números que já existem: features com drift
   (PSI/KS) por janela, deslocamento do score e queda de AUC.
3. **Separar data drift de concept drift com os próprios dados:**
   - de t1 a t3 só há data drift: AUC 0,924 → 0,891;
   - de t3 a t5 entra o concept drift: AUC 0,891 → 0,801.
4. **Correlação × causalidade:**
   - aqui sabemos a causa porque a simulação é uma intervenção controlada;
   - em produção, o monitoramento só vê associação. Confirmar a causa exigiria cruzar com
     indicadores externos (IPCA, Selic, desemprego) e testes contrafactuais.
5. **Prescrição:**
   - retreinar com rótulos recentes;
   - recalibrar o score;
   - revisar o corte de aprovação;
   - usar renda real (deflacionada);
   - ampliar o contrato (faixa plausível de `loan_int_rate`).

   Para cada ação, dizer quem decide.

**Commits sugeridos**

- `docs(governance): documenta mitigação de vieses com o relatório de fairness`
- `docs(governance): adiciona análise causal da degradação do modelo`

### W4. README consolidado (T4.5)

- **Começo rápido:** `uv sync` → download → `run_pipeline.py` → abrir
  `reports/monitoring/index.html`.
- **Mapa de evidências por critério de avaliação:** contratos, drift, observabilidade,
  governança e vídeo, cada um com link para o arquivo.
- **Seção "Equipe"** com nomes e RMs (os mesmos já publicados na descrição do vídeo da
  Fase 1).
- **Corrigir** "12 violações" para 8 e revisar números citados contra os artefatos.
- **Pendência da D7:** verificar a licença do dataset no Kaggle. Se permitir, versionar o
  CSV bruto para o avaliador rodar sem conta no Kaggle.

**Commit sugerido:** `docs: consolida execução e mapa de evidências no readme`

### W5. CI (T0.6)

- `.github/workflows/ci.yml`: `setup-uv` → `uv sync --frozen` → `ruff check` →
  `ruff format --check` → `pytest`. Os testes já rodam sem dados reais: 119 passaram nesta
  máquina sem `data/` nem `models/`.
- Antes do CI, formatar os 2 arquivos pendentes.

**Commits sugeridos**

- `style: aplica ruff format nos arquivos pendentes`
- `ci: executa lint e testes em cada pull request`

### W6. Vídeo STAR (T4.6, T4.7)

Detalhado na seção 5.

**Commits sugeridos**

- `docs(governance): adiciona roteiro do vídeo star`
- `docs: adiciona link do vídeo star no readme`

## 5. Plano do vídeo

### O que aprendemos com os vídeos anteriores do grupo

| Vídeo | Duração | O que funcionou | O que evitar |
|---|---|---|---|
| Fase 1, churn (Vini) | **5:51** ❌ | situação de negócio bem explicada | ~2 min de "tour" pelas pastas do repositório; demo da API no fim estourou o tempo; o roteiro previa 5:00 |
| Fase 2, recomendação (Fernando) | 4:38 ✅ | STAR explícito; demo de ~2 min; resultado com números concretos | ~10 s lendo os nomes em voz alta |
| Fase 3, laudos (Eduardo) | 4:48 ✅ | arquitetura e Grafana bem mostrados | rótulos STAR não ditos; trechos de demo com pouca narração |

Conclusões:

- Nenhum dos três teve **"lições aprendidas"**, e desta vez o enunciado exige isso no
  Result.
- Vitor é o único que ainda não apresentou, e é o dono da Etapa 4.

### Regras de produção

- **Meta de 4:30 de fala**, cerca de 650 palavras a ~150 palavras/min. Isso deixa ~30 s de
  folga para o limite de 4:59.
- **Nada de tour de pastas.** Abrir só as evidências: terminal, HTML do Evidently, painel,
  README de governança.
- **Comandos já executados antes de gravar.** O `run_pipeline.py` é lento demais para ao
  vivo. No terminal, mostrar só o bloqueio do contrato, que é rápido.
- Abas abertas na ordem do roteiro, zoom no navegador e no terminal.
- Nomes e RMs **no slide de abertura**, não lidos em voz alta.
- Dizer em voz alta "Situação", "Tarefa", "Ação", "Resultado", como fez o vídeo da Fase 2.
- Gravar por blocos e editar. **Conferir a duração final no editor antes de subir.**
- YouTube como "Não listado", com descrição contendo integrantes, RMs e link do GitHub.

### Cronograma (4:30)

| Bloco | Tempo | Na tela | Conteúdo obrigatório |
|---|---|---|---|
| Abertura | 0:00–0:15 | slide título + integrantes | gancho: o modelo não quebra com erro na tela, ele continua respondendo, só que errado |
| **S** | 0:15–0:45 | slide | degradação silenciosa; inflação e juros mudam o perfil do cliente; custo de aprovar quem não paga e negar quem paga |
| **T** | 0:45–1:10 | slide com 3 colunas | interceptar dados ruins · detectar drift (data + concept) · garantir compliance (LGPD, vieses) |
| **A1** contrato | 1:10–1:35 | terminal | Pandera com regras rígidas; `validate_data.py --make-bad-batch` → **exit code 1** e regras violadas |
| **A2** simulação | 1:35–2:00 | tabela t1–t5 | 4 features alteradas com justificativa econômica; concept drift em t4 e t5; seed fixa |
| **A3** observabilidade | 2:00–2:25 | fluxo da arquitetura | Evidently (PSI + KS), logs sem PII, regras de alerta, painel HTML e Prometheus/Grafana |
| **A4** governança | 2:25–2:55 | README (governança) | pseudonimização, base legal (art. 7º, X e art. 20), retenção, fairness, diagrama causal |
| **R1** drift | 2:55–3:30 | `drift_t5.html` + painel | features degradadas apontadas; AUC 0,942 → 0,801; score médio dobra |
| **R2** alertas | 3:30–3:50 | tabela de alertas / Grafana | `bad_batch` crítico; t3 em atenção; t4 e t5 críticos |
| **R3** lições | 3:50–4:20 | slide | PSI × KS (renda só aparece no KS); KS sensível com amostras grandes, por isso o alerta usa a proporção de features; score como sinal antecipado do concept drift; governança desde o início |
| Fechamento | 4:20–4:30 | slide | próximos passos (retreino com rótulos recentes, renda deflacionada) e agradecimento |

O roteiro completo, com a fala de cada bloco, é o entregável da T4.6
(`docs/roteiro-video-star.md`).

## 6. Decisões a tomar

Registrar as respostas no "Registro de decisões" de `context/01-arquitetura.md`.

| # | Decisão | Recomendação | Por quê |
|---|---|---|---|
| D8 | Base e grupos do relatório de vieses | holdout de 20% da Referência; faixa etária + `person_home_ownership`; alerta com razão < 0,8 | mesma base das métricas do baseline; grupos sugeridos no stub |
| D9 | `person_age` no modelo | **manter** e documentar o risco e o resultado do fairness | retreinar sem idade refaria todas as evidências das Etapas 1–3; a importância é de 1,4% |
| D10 | `loan_intent = MEDICAL` (possível dado de saúde) | manter, documentar como dado sensível e justificar a finalidade | é a finalidade do empréstimo, não um diagnóstico; remover mudaria o modelo |
| D11 | Integração antes da Etapa 4 | PR `feat/step-3 → main` primeiro | evita a Etapa 4 nascer de uma branch não revisada |
| D12 | Apresentação do vídeo | Vitor apresenta, com demos pré-gravadas | dono da Etapa 4 e único que ainda não apresentou |
| D13 | Profundidade da análise causal | só documentação, usando os números existentes; experimento de intervenção como extra | o enunciado pede documentação e os números já separam data drift de concept drift |

## 7. Cronograma até a entrega e ordem de execução

| Dia | Manhã/tarde | Noite | Pronto quando |
|---|---|---|---|
| **15/11 (dom)** | pré-requisitos (PR step-3 → main, branch, dados locais) · **W1** fairness | **W2** PII, base legal e retenção no README | `run_pipeline.py` roda inteiro; `fairness.csv` gerado |
| **16/11 (seg)** | **W3** vieses e causal · **W4** README consolidado · execução final dos artefatos | **W6** roteiro, slides e ensaio cronometrado | README de governança completo; roteiro com ≤ 4:30 no ensaio |
| **17/11 (ter)** | gravação, edição, upload no YouTube e link no README | **T4.8** revisão final e PR | vídeo < 4:59 publicado; checklist 100% |

**Cortar primeiro se faltar tempo** (não pontuam ou são extras):

1. W5 (CI): o T0.6 é boa prática, mas não está no enunciado;
2. `fairness_windows.csv`;
3. experimento de intervenção da D13;
4. versionar o CSV bruto (D7).

```
Pré-requisitos (PR step-3 → main, branch, dados locais)
   │
   ├─► W1 Fairness (código) ──► pipeline volta a rodar ──► execução final + versionar artefatos
   │        │
   │        └─► W3 Vieses e causal (README)
   ├─► W2 PII, base legal e retenção (README)        ← pode começar já, em paralelo
   ├─► W5 CI                                          ← independente
   │
   └─► W4 README consolidado ──► W6 roteiro ──► ensaio cronometrado ──► gravação ──► link
                                                                                   │
                                                              T4.8 revisão final ◄─┘
```

- **Dependência crítica:** W1 antes do vídeo, porque a demo precisa do pipeline inteiro
  funcionando.
- **Revisão final (T4.8):** rodar `/checklist` e o agente `tc-reviewer`, marcar
  `context/03-checklist-entregaveis.md` e o `TODO.md`, e abrir o PR final.

## 8. Riscos

| Risco | Mitigação |
|---|---|
| Vídeo passar de 4:59 | meta de 4:30, ensaio cronometrado e conferência no editor |
| Sem acesso ao Kaggle para gerar o `fairness.csv` | pedir o CSV bruto a um colega ou versioná-lo, se a licença permitir |
| Execução final mudar números já citados no README | seed fixa e salt fixo; reconferir as tabelas após a execução final |
| Citação jurídica imprecisa | conferir artigos e prazos na fonte oficial antes de publicar |
| CI quebrar no primeiro PR | formatar os 2 arquivos antes de ativar o workflow |
