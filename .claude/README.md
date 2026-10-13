# .claude/: configuração do Claude Code

Esta pasta guarda **apenas** o que é específico do Claude Code:

| Caminho | O que é |
|---|---|
| `settings.json` | Permissões compartilhadas do projeto (versionado) |
| `settings.local.json` | Ajustes pessoais (**não** versionado) |
| `commands/` | Comandos `/checklist`, `/commit`, `/etapa` (pares em `.github/prompts/`) |
| `agents/` | Subagente `tc-reviewer` (par: `.github/prompts/revisar.prompt.md`) |

> 📌 **O contexto do projeto NÃO fica aqui.** Ele mora na pasta [`context/`](../context/README.md)
> da raiz, que é **única e exclusiva para o contexto compartilhado** entre Claude Code e
> GitHub Copilot. O `CLAUDE.md` da raiz importa essa pasta. Regras do projeto vão em
> `context/`. Aqui vão só as configurações e os comandos do Claude.
