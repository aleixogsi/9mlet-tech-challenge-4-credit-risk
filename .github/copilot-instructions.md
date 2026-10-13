# Instruções do GitHub Copilot: Tech Challenge Fase 4 (Credit Risk)

Projeto do **Tech Challenge da Fase 4 (MLET / FIAP Pós Tech)**: camada de **sustentação e
confiabilidade** de um modelo de Credit Scoring de uma fintech. Escopo: contratos de
qualidade de dados, simulação e detecção de Data/Concept Drift, observabilidade e
governança LGPD com análise causal.

## Pasta `context/` (contexto compartilhado)

A pasta `context/` na raiz é **única e exclusiva para o contexto compartilhado** entre
GitHub Copilot e Claude Code. Ela é a fonte única das regras do projeto para as IAs.

- Não crie em `context/` documentação do projeto, relatórios ou qualquer outro material.
  Documentação vai em `docs/` e relatórios em `reports/`.
- Não confunda `context/` com `docs/`: `docs/` é documentação do projeto e **não** é
  contexto de IA.
- Configurações específicas do Copilot ficam em `.github/copilot-instructions.md`,
  `.github/instructions/` e `.github/prompts/`, nunca em `context/`.
- Ao alterar algo em `context/`, lembre que isso afeta também o Claude Code.

## Fonte da verdade

O enunciado oficial está em [context/00-tech-challenge.md](../context/00-tech-challenge.md)
e **tem prioridade sobre qualquer outra decisão**. Se um pedido contrariar o enunciado,
avise antes de implementar.

Contexto complementar (consulte quando for relevante):

- [context/01-arquitetura.md](../context/01-arquitetura.md): pipeline, estrutura de pastas, entrypoints, registro de decisões
- [context/02-convencoes.md](../context/02-convencoes.md): código, testes, commits, branches
- [context/03-checklist-entregaveis.md](../context/03-checklist-entregaveis.md): progresso dos requisitos
- [context/04-governanca-lgpd.md](../context/04-governanca-lgpd.md): guia da seção de Governança/LGPD
- [context/05-interfaces.md](../context/05-interfaces.md): formatos congelados dos artefatos trocados entre as trilhas

## Etapas e pesos de avaliação

1. **Validação de Dados (25%)**: baseline treinado com o dataset de Referência; contrato
   Pandera/Great Expectations com ≥ 3 regras rígidas (ex.: idade > 18, renda não nula, sem
   duplicatas); um lote com erros **falha e é bloqueado**.
2. **Detecção de Drift (25%)**: dataset de Produção simulando o tempo, com ≥ 2 features
   importantes alteradas; predições; Evidently Referência × Produção; PSI/KS; relatório
   HTML apontando as features degradadas.
3. **Observabilidade (20%)**: logs de predição e resultados de drift centralizados;
   dashboard (Prometheus + Grafana) ou relatórios Evidently automatizados; métricas de
   saúde (% predições nulas, latência, volume, nº de alertas).
4. **Governança LGPD (15%)**, no README: tratamento de PII, base legal, retenção,
   mitigação de vieses e análise causal.
5. **Vídeo STAR (15%)**: ≤ 5 min.

## Regras essenciais

- **Stack obrigatória:** Scikit-Learn/XGBoost, Pandera ou Great Expectations, Evidently
  AI. Prometheus-client é opcional.
- **Referência × Produção** sempre separados. Nunca treinar com dados de produção.
- O contrato **bloqueia** a ingestão (exceção ou exit code ≠ 0).
- O drift simulado cobre data drift **e** concept drift, é reprodutível (seed fixa) e é
  medido com PSI/KS.
- Caminhos, seeds e thresholds ficam em `src/credit_risk/config.py`. Nada de valores mágicos.
- Relatórios HTML em `reports/` são versionados. `data/` e `.env` **nunca**.
- Sem PII em logs, commits ou relatórios.
- Código em inglês. Docs, relatórios e mensagens de commit em pt-BR.
- Python 3.11+, type hints, `ruff`, `pytest`, `logging` em vez de `print` em `src/`.
- **Commits semânticos** (Conventional Commits em pt-BR) são critério de avaliação.
  Ex.: `feat(contracts): adiciona regra de idade mínima`.
- Decisões tomadas: **Credit Risk Dataset (Kaggle)**, **Pandera**, **XGBoost**,
  **Evidently + painel HTML** e **uv**. Ver "Registro de decisões" em `01-arquitetura.md`.
  Novas decisões: **não assuma; pergunte e registre.**
- **Tarefas:** o backlog e a divisão da equipe estão em `TODO.md` (IDs T0.1…T4.8). No
  código, cada stub tem `TODO(<ID>)` e lança `NotImplementedError("<ID>")`. Ao implementar
  uma tarefa, siga o docstring do stub e mantenha as assinaturas (são interfaces entre as
  trilhas). Ao concluir, atualize o status no `TODO.md`.
- **Trabalho assíncrono:** os formatos de arquivos trocados entre as trilhas estão congelados em
  `context/05-interfaces.md`. Nunca mude esses formatos sem avisar. Se a parte de outra trilha
  ainda não existe, use os dados sintéticos (`tests/fixtures/synthetic.py`) e os mocks
  (`tests/fixtures/mocks/`) em vez de esperar ou implementar a parte do colega.

## Comandos úteis

```bash
uv sync                                   # instala as dependências
uv run pytest                             # testes
uv run ruff check . && uv run ruff format .
uv run python scripts/run_pipeline.py     # pipeline ponta a ponta
```

## Mensagens de commit geradas pelo Copilot

Formato `<tipo>(<escopo>): <descrição>` em pt-BR, no imperativo, minúscula, sem ponto
final. Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`. Escopos: `contracts`,
`training`, `drift`, `monitoring`, `governance`, `data`, `context`.

## Equipe e ferramentas

Parte do grupo usa **Claude Code**, cujo contexto equivalente está em `CLAUDE.md` e
`.claude/`. Ao alterar uma regra central aqui, atualize também `CLAUDE.md`. Os prompts de
`.github/prompts/` têm equivalentes em `.claude/commands/`.
