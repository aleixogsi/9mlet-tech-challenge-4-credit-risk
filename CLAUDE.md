# CLAUDE.md

Projeto do **Tech Challenge da Fase 4 (MLET / FIAP Pós Tech)**: camada de **sustentação e
confiabilidade** de um modelo de Credit Scoring de uma fintech. Escopo: contratos de
qualidade de dados, simulação e detecção de Data/Concept Drift, observabilidade e
governança LGPD com análise causal.

## Pasta `context/` (contexto compartilhado)

A pasta `context/` na raiz é **única e exclusiva para o contexto compartilhado** entre
Claude Code e GitHub Copilot. Ela é a fonte única das regras do projeto para as IAs.

- Não crie em `context/` documentação do projeto, relatórios ou qualquer outro material.
  Documentação vai em `docs/` e relatórios em `reports/`.
- Não confunda `context/` com `docs/`: `docs/` é documentação do projeto e **não** é
  contexto de IA.
- Configurações específicas do Claude ficam em `CLAUDE.md` e `.claude/`, nunca em `context/`.
- Ao alterar algo em `context/`, lembre que isso afeta também o Copilot.

## Fonte da verdade

O enunciado oficial está transcrito em `context/00-tech-challenge.md`. **Ele tem
prioridade sobre qualquer outra decisão.** Se um pedido contrariar o enunciado, avise antes
de implementar.

@context/00-tech-challenge.md
@context/01-arquitetura.md
@context/02-convencoes.md
@context/05-interfaces.md

Leia sob demanda:

- `context/03-checklist-entregaveis.md`: progresso dos requisitos (atualize ao concluir itens)
- `context/04-governanca-lgpd.md`: ao escrever a seção de Governança/LGPD do README

## Regras essenciais

- **Stack obrigatória:** Scikit-Learn/XGBoost (modelo), Pandera ou Great Expectations
  (contratos), Evidently AI (drift e relatórios). Prometheus-client é opcional.
- **Referência × Produção** sempre separados. Nunca treinar com dados de produção.
- O contrato de dados **bloqueia** a ingestão (exceção ou exit code ≠ 0), com **≥ 3 regras rígidas**.
- O drift simulado altera **≥ 2 features importantes**, cobre data drift **e** concept
  drift, é reprodutível (seed) e é medido com **PSI/KS**.
- Relatórios HTML em `reports/` são entregáveis e **são versionados**. `data/` e `.env` **nunca**.
- Sem PII em logs, commits ou relatórios.
- Código em inglês. Docs, relatórios e commits em pt-BR.
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

## Equipe e ferramentas

Parte do grupo usa **VS Code + GitHub Copilot**, cujo contexto equivalente fica em
`.github/`. Ao alterar uma regra central aqui, atualize também
`.github/copilot-instructions.md`. Os comandos de `.claude/commands/` têm equivalentes em
`.github/prompts/` e devem ficar sincronizados.

## Comandos úteis

```bash
uv sync                                   # instala as dependências
uv run pytest                             # testes
uv run ruff check . && uv run ruff format .
uv run python scripts/run_pipeline.py     # pipeline ponta a ponta
```
