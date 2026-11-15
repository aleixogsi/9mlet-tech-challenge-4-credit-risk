# Plano de desenvolvimento da Etapa 4: Governança e vídeo STAR

> Responsável: Vitor (ver [TODO.md](../TODO.md)). Base: enunciado oficial (PDF, p. 5–6) e
> estado da branch `feat/step-3` em 15/11/2026.
>
> ⏰ **Entrega: 17/11/2026** (prazo registrado em outubro; confirmar com o grupo). O plano é
> executado **numa tacada só**, sem cronograma por dias: o Claude executa as frentes de
> trabalho e o Vitor revisa, commita e grava o vídeo em seguida. A prioridade segue o peso
> na nota: Governança (15%) e Vídeo (15%). Itens que não pontuam (CI, extras) só entram se
> sobrar tempo. Ver a ordem de execução na seção 7.

> ✅ **Execução (15/11/2026):** T4.1 a T4.6 e T0.6 concluídas. Dos problemas da seção 2,
> os itens 1 a 6 e o 8 foram resolvidos (os itens 5 e 6 viraram as decisões D10 e D9). O que
> resta: integrar as branches na `main` (item 7, via PR), gravar o vídeo e pôr o link no
> README (T4.7) e conferir o vídeo na revisão final (T4.8). As seções abaixo guardam o
> diagnóstico de antes da execução.

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
| T4.6 | Roteiro do vídeo | não existe; o deck e a página de demonstração (W7) já estão prontos ou aprovados |
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
6. **`person_age` é feature do modelo** (1,5% da importância). Idade é atributo com risco
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

A única frente com código do repositório é a W1. As outras são documentação, CI, vídeo e
o material de apresentação (W7), que fica fora do Git.

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
   - de t1 a t3 só há data drift: AUC 0,929 → 0,892;
   - de t3 a t5 entra o concept drift: AUC 0,892 → 0,806.
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

Detalhado na seção 5. O roteiro (`docs/roteiro-video-star.md`) traz a fala de cada bloco,
o que aparece na tela (slide, página ou evidência) e o tempo de cada trecho.

**Commits sugeridos**

- `docs(governance): adiciona roteiro do vídeo star`
- `docs: adiciona link do vídeo star no readme`

### W7. Material de apresentação (local, fora do Git)

Fica na pasta `apresentacao/` na raiz do repositório, excluída do Git via
`.git/info/exclude`. Serve só para gravar o vídeo; nada aqui é entregável do repositório.

**Deck STAR: pronto.** `apresentacao/Tech_Challenge_4_STAR.pptx`, gerado por
`apresentacao/build_deck.py`, com a identidade visual do vídeo da Fase 2 (Fernando).
São 11 slides com as falas nas notas:

| # | Slide | Uso no vídeo |
|---|---|---|
| 1–2 | Capa e participantes (fotos, RMs, etapa de cada um) | abertura |
| 3 | Situation: o cenário proposto pelo desafio | S |
| 4 | Task: interceptar, detectar, garantir compliance | T |
| 5–7 | Action: arquitetura, simulação t1–t5, governança e cadeia causal | A |
| 8–9 | Results: AUC por janela e mapa de alertas | **reserva**, se a página falhar |
| 10 | Lições aprendidas e próximos passos | R |
| 11 | Obrigado | fechamento |

**Página de demonstração: visual aprovado (15/11/2026), falta construir.**
`apresentacao/demo/index.html`. O visual é de app de banco, com a marca fictícia
"vértice": o celular do cliente à esquerda e a Central de Risco à direita, em 1600×900
para gravar em 16:9. Os prints aprovados estão em `apresentacao/demo/shots/`. São 5 cenas,
trocadas pelas setas do teclado:

| Cena | Celular | Central de Risco |
|---|---|---|
| 1. Produção normal | cliente sorteado de t1 ao vivo ("Atualizar dados"); "Pedir análise" passa pelo contrato e pelo modelo (D17) | KPIs, esteira (contrato → modelo → decisão), log só com hash, card de privacidade |
| 2. Lote inválido | notificação "Ingestão bloqueada" | regras violadas, exit code 1, modelo sem registros, lotes validados |
| 3. A economia muda | termômetro da economia (parâmetros de t5) | features com drift por janela, curva de juros Referência × t5, PSI/KS por feature, cadeia causal |
| 4. Degradação silenciosa | cliente de t5 aprovado com risco baixo e, uns 3 s depois, o aviso "6 meses depois: parcelas em atraso" (degradação forçada, D17) | saúde operacional verde × AUC caindo de 0,927 para 0,806 |
| 5. Alertas | notificações críticas de t5 | os 9 alertas reais, alertas por janela, prescrição e atalhos para Evidently e Grafana |

O que falta na página:

1. **Animações por cena:** propostas deslizando pela esteira, contadores subindo, curva de
   produção se afastando da referência, linha da AUC sendo desenhada, alertas entrando um
   a um.
2. **Modo replay** (garantia): um script local gera um arquivo de dados a partir de
   `logs/predictions.jsonl`, `logs/alerts.jsonl`, `logs/validation.jsonl` e
   `reports/drift/drift_summary.json`, e a página toca esses dados reais sem servidor.
3. **Modo ao vivo:** uma mini-API local carrega `models/baseline_v1.joblib`, passa cada
   proposta pelo contrato e devolve score e latência reais para a cena 1.
4. **Trocar o ilustrativo pelo real:** as curvas de juros da cena 3 e as linhas da tabela
   de predições da cena 1 vêm hoje de valores de exemplo. Com `data/` gerado localmente,
   passam a vir dos histogramas e das predições reais.

**Pronto quando:** a página abre com duplo clique (modo replay), as 5 cenas animam na
ordem do roteiro e, com a API no ar, a cena 1 mostra predições do modelo real.

**Commits:** nenhum (pasta fora do Git).

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
- **Nada de tour de pastas.** Abrir só as evidências: HTML do Evidently, painel (com o
  contrato rodando dentro dele) e README de governança.
- **Comandos já executados antes de gravar.** O `run_pipeline.py` é lento demais para ao
  vivo. Ao vivo, só o bloqueio do contrato, que é rápido e roda pelo botão "Testar lote
  com erro" da página (D18), sem trocar de janela.
- Abas abertas na ordem do roteiro e zoom no navegador.
- Nomes e RMs **no slide de abertura**, não lidos em voz alta.
- Dizer em voz alta "Situação", "Tarefa", "Ação", "Resultado", como fez o vídeo da Fase 2.
- **Situation é o cenário proposto pelo desafio** (a fintech, a economia mudando, a suspeita
  da diretoria e o risco da degradação silenciosa), não o estado do nosso projeto. O que
  construímos entra a partir da Action.
- **Deixar claro, sem insistir, que o modelo é bom e a queda é simulada.** Sem esse
  contexto, a cena 4 passa a impressão de um modelo fraco. Basta citar a AUC de 0,927 do
  modelo base na A1 e chamar t5 de "crise simulada" no R1; a página já traz os mesmos
  rótulos (cena 1: "baseline_v1 · AUC 0,927"; cena 4: "crise simulada" e "modelo base
  0,927").
- **A página de demonstração (W7) mostra; a evidência prova.** A página conduz as partes A
  e R, mas o vídeo também mostra a saída real do contrato com o `exit code 1` e o HTML real
  do Evidently,
  que é o que o enunciado pede no Result.
- Gravar por blocos e editar. **Conferir a duração final no editor antes de subir.**
- YouTube como "Não listado", com descrição contendo integrantes, RMs e link do GitHub.

### Cronograma (4:30)

| Bloco | Tempo | Na tela | Conteúdo obrigatório |
|---|---|---|---|
| Abertura | 0:00–0:15 | slides 1–2 (capa e participantes) | tema do projeto; nomes e RMs ficam no slide, sem leitura em voz alta |
| **S** | 0:15–0:45 | slide 3 | o cenário do desafio: fintech com Credit Scoring em produção; inflação e novos perfis de clientes; a diretoria suspeita de decisões erradas; risco de degradação silenciosa |
| **T** | 0:45–1:05 | slide 4 | interceptar dados ruins · detectar drift (data + concept) · garantir compliance (LGPD, vieses) |
| **A1** arquitetura | 1:05–1:30 | slide 5 → página, cena 1 | a camada de sustentação ponta a ponta; o modelo respondendo ao vivo (citar de passagem a AUC de 0,927 do modelo base); log só com hash |
| **A2** contrato | 1:30–1:50 | página, cena 1 (botão do contrato) → cena 2 | Pandera com regras rígidas; `validate_data.py --make-bad-batch` → **exit code 1** e regras violadas |
| **A3** simulação | 1:50–2:15 | slide 6 → página, cena 3 | 4 features alteradas com justificativa econômica; concept drift em t4 e t5; seed fixa; PSI e KS do Evidently |
| **A4** governança | 2:15–2:45 | slide 7 + README (governança) | pseudonimização, base legal (art. 7º, X e art. 20), retenção, fairness, cadeia causal |
| **R1** drift | 2:45–3:25 | página, cena 4 → `drift_t5.html` | operação verde e decisão pior; features degradadas apontadas no Evidently; AUC 0,927 → 0,806 na crise que simulamos |
| **R2** alertas | 3:25–3:45 | página, cena 5 (Grafana opcional) | `bad_batch` crítico; t3 crítica pelo data drift e em atenção pelo score; t4 e t5 críticos; prescrição |
| **R3** lições | 3:45–4:15 | slide 10 | PSI × KS (renda só aparece no KS); KS sensível com amostras grandes, por isso o alerta usa a proporção de features; score como sinal antecipado do concept drift; governança desde o início |
| Fechamento | 4:15–4:30 | slide 11 | próximos passos (retreino com rótulos recentes, renda deflacionada) e agradecimento |

Os slides 8 e 9 ficam de reserva: se a página falhar na gravação, eles cobrem R1 e R2.

O roteiro completo, com a fala de cada bloco, é o entregável da T4.6
(`docs/roteiro-video-star.md`).

## 6. Decisões a tomar

Registrar as respostas no "Registro de decisões" de `context/01-arquitetura.md`.

| # | Decisão | Recomendação | Por quê |
|---|---|---|---|
| D8 | Base e grupos do relatório de vieses | holdout de 20% da Referência; faixa etária + `person_home_ownership`; alerta com razão < 0,8 | mesma base das métricas do baseline; grupos sugeridos no stub |
| D9 | `person_age` no modelo | **manter** e documentar o risco e o resultado do fairness | retreinar sem idade refaria todas as evidências das Etapas 1–3; a importância é de 1,5% |
| D10 | `loan_intent = MEDICAL` (possível dado de saúde) | manter, documentar como dado sensível e justificar a finalidade | é a finalidade do empréstimo, não um diagnóstico; remover mudaria o modelo |
| D11 | Integração antes da Etapa 4 | PR `feat/step-3 → main` primeiro | evita a Etapa 4 nascer de uma branch não revisada |
| D12 | Apresentação do vídeo | Vitor apresenta, com demos pré-gravadas | dono da Etapa 4 e único que ainda não apresentou |
| D13 | Profundidade da análise causal | só documentação, usando os números existentes; experimento de intervenção como extra | o enunciado pede documentação e os números já separam data drift de concept drift |
| D14 | Material de apresentação | **Decidido (15/11/2026):** deck STAR com a identidade da Fase 2 e página de demonstração com visual de app de banco, ambos locais em `apresentacao/`, fora do Git | apoiam o vídeo sem virar entregável; o visual da página foi aprovado pelo Vitor |

## 7. Ordem de execução (numa tacada só)

Tudo é executado de uma vez, na ordem abaixo. A coluna "Depende de" separa o que roda
sem dados locais do que precisa do dataset baixado.

| Ordem | O quê | Quem | Depende de | Pronto quando |
|---|---|---|---|---|
| 0 | Deck STAR (W7) | Claude | — | ✅ pronto |
| 1 | **W1** fairness: código e testes com dados sintéticos | Claude | — | testes passando |
| 2 | Dados locais: `download_data.py` → `prepare_data.py` → `train_baseline.py` | Claude | Kaggle (**autorização do Vitor**) | `data/` e modelo gerados |
| 3 | `bias_report.py` e execução final do `run_pipeline.py` | Claude | ordem 2 | `fairness.csv` gerado; pipeline roda inteiro |
| 4 | **W2** PII, base legal e retenção no README | Claude | — | seções T4.1 e T4.2 escritas |
| 5 | **W3** vieses e análise causal no README | Claude | ordem 3 (tabela de fairness) | seções T4.3 e T4.4 escritas |
| 6 | **W4** README consolidado e números conferidos | Claude | ordens 4 e 5 | começo rápido, mapa de evidências e "8 violações" |
| 7 | **W6** roteiro do vídeo (`docs/roteiro-video-star.md`) | Claude | ordem 6 | fala com ≤ 4:30 na leitura |
| 8 | **W7** página: animações e modo replay | Claude | — | as 5 cenas animam com dados reais |
| 9 | **W7** página: modo ao vivo e curvas reais | Claude | ordem 2 | cena 1 com predições do modelo real |
| 10 | **W5** CI | Claude | — | workflow verde |
| 11 | Revisar, commitar, abrir o PR | **Vitor** | ordens 1–10 | commits semânticos na `feat/etapa4-governanca` |
| 12 | Ensaiar, gravar, editar, publicar e pôr o link no README | **Vitor** | ordens 7–9 | vídeo < 4:59 no YouTube |
| 13 | **T4.8** revisão final | Claude + Vitor | ordem 12 | checklist 100% |

Sem autorização para o Kaggle, as ordens 2, 3, 5 (parte da tabela) e 9 ficam para depois.
O resto segue com dados sintéticos e com os artefatos já versionados. Os commits ficam com
o Vitor; o Claude deixa a sequência de mensagens pronta.

**Cortar primeiro se faltar tempo** (não pontuam ou são extras):

1. W5 (CI): o T0.6 é boa prática, mas não está no enunciado;
2. modo ao vivo da página (o replay com dados reais basta para o vídeo);
3. `fairness_windows.csv`;
4. experimento de intervenção da D13;
5. versionar o CSV bruto (D7).

```
Pré-requisitos (PR step-3 → main, branch, dados locais)
   │
   ├─► W1 Fairness (código) ──► pipeline volta a rodar ──► execução final + versionar artefatos
   │        │
   │        └─► W3 Vieses e causal (README)
   ├─► W2 PII, base legal e retenção (README)        ← pode começar já, em paralelo
   ├─► W5 CI                                          ← independente
   ├─► W7 página: animações + replay                  ← independente
   │        └─► (com dados locais) modo ao vivo + curvas reais
   │
   └─► W4 README consolidado ──► W6 roteiro ──► ensaio cronometrado ──► gravação ──► link
                                    ▲                                              │
                      deck pronto + página (W7)               T4.8 revisão final ◄─┘
```

- **Dependência crítica:** W1 antes do vídeo, porque a demo precisa do pipeline inteiro
  funcionando.
- **A página não bloqueia o vídeo:** se ela não ficar pronta, os slides 8 e 9 cobrem R1 e R2.
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
| Página de demonstração falhar na hora de gravar | modo replay sem servidor; slides 8 e 9 de reserva |
| Página mostrar número diferente dos artefatos | a página lê os logs e o `drift_summary.json` reais em vez de números digitados |
