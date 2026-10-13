# Convenções de código e de trabalho em equipe

Vale para todos os integrantes, seja escrevendo à mão, com Claude Code ou com GitHub Copilot.

## Idioma

- **Documentação, README, relatórios e mensagens de commit:** português (pt-BR).
- **Código** (nomes de variáveis, funções, classes, módulos): inglês.
- **Docstrings e comentários:** português ou inglês, desde que consistentes dentro do
  mesmo módulo.

## Python

- Python 3.11+.
- Type hints em funções públicas.
- Formatação e lint com `ruff` (format + check).
- Funções pequenas e puras sempre que possível. I/O (ler/gravar arquivos) fica nos
  `scripts/` ou em funções de borda bem identificadas.
- Nada de caminhos absolutos nem "números mágicos": caminhos, seeds e thresholds ficam em
  `src/credit_risk/config.py`.
- Use `logging` (não `print`) nos módulos de `src/`.
- Aleatoriedade sempre com seed (`random_state`, `np.random.default_rng(seed)`).
- Sem notebooks no repositório (o enunciado não pede). Toda análise vira script em `scripts/` com saída em `reports/`.

## Testes

- `pytest` em `tests/`, espelhando a estrutura de `src/`.
- Obrigatório testar:
  - **contratos:** um dataset válido passa, e cada regra rígida falha com o lote ruim
    correspondente;
  - **simulação de drift:** a feature alterada muda de distribuição de fato (ex.: PSI > threshold);
  - **detecção:** dados idênticos → sem drift; feature deslocada → drift detectado.

## Dados e privacidade (LGPD by default)

- **Nunca** versionar dados (`data/` fica no `.gitignore`) nem arquivos com PII. Única
  exceção: o CSV bruto público, se a licença permitir (T0.2).
- `logs/` só é commitado na execução final (T3.8). Durante o desenvolvimento, não commite logs.
- Nunca logar PII em `logs/`. Use identificadores pseudonimizados (hash com salt) quando
  precisar rastrear uma predição.
- Remover ou não usar como feature colunas sensíveis ou proxies de atributos protegidos
  (ex.: nome, CPF, endereço completo, gênero, raça, estado civil) sem justificativa
  documentada. Use-as **apenas** para análise de viés/fairness, se necessário.
- Segredos (tokens do Kaggle etc.) ficam em `.env`, que nunca é commitado.

## Git

### Commits semânticos (requisito avaliado)

Formato [Conventional Commits](https://www.conventionalcommits.org/pt-br/), com a
mensagem em português:

```
<tipo>(<escopo opcional>): <descrição no imperativo, minúscula, sem ponto final>
```

| Tipo | Uso |
|---|---|
| `feat` | nova funcionalidade (novo contrato, script, relatório) |
| `fix` | correção de bug |
| `docs` | documentação (README, docs/, LGPD) |
| `test` | testes |
| `refactor` | refatoração sem mudar comportamento |
| `chore` | configuração, dependências, tooling |
| `ci` | pipelines de CI |
| `data` | scripts/parâmetros de dados e simulação (opcional, se o grupo adotar) |

Escopos sugeridos: `contracts`, `training`, `drift`, `monitoring`, `governance`,
`data`, `context` (arquivos de contexto de IA).

Exemplos:

- `feat(contracts): adiciona schema pandera com regras de idade, renda e duplicatas`
- `feat(drift): simula inflação na renda e aumento de desemprego em 6 janelas`
- `docs(governance): adiciona plano de retenção e base legal LGPD`

Regras:

- Um commit = uma mudança lógica. Nada de "update" ou "ajustes" genéricos.
- Nunca commitar `data/`, `.env` ou arquivos grandes de modelo.

### Branches

- `main` protegida, sempre funcional.
- Branches de trabalho: `feat/<etapa>-<descricao>`, `fix/...`, `docs/...`.
  Ex.: `feat/etapa1-contratos`.
- Entrar na `main` via Pull Request, com revisão de pelo menos 1 colega.

## Contexto de IA (Claude Code + Copilot)

- O contexto compartilhado mora em `context/`. **Edite aqui**, não nos arquivos
  específicos de cada ferramenta.
- `context/` é **única e exclusiva para o contexto compartilhado das IAs**. Documentação
  do projeto vai em `docs/`, relatórios em `reports/`.
- `CLAUDE.md` e `.github/copilot-instructions.md` são resumos que apontam para
  `context/`. Ao mudar uma regra importante, **atualize os dois**.
- Comandos equivalentes:
  - Claude: `.claude/commands/<nome>.md` → `/<nome>`
  - Copilot: `.github/prompts/<nome>.prompt.md` → `/<nome>` no Copilot Chat
  - Mantenha os pares sincronizados.
