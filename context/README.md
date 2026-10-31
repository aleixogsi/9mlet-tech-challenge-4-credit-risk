# context/: contexto compartilhado para assistentes de IA

> ⚠️ **Pasta de uso ÚNICO E EXCLUSIVO para o contexto compartilhado entre as IAs**
> (Claude Code e GitHub Copilot).
>
> - **Não** coloque aqui documentação do projeto, relatórios, notebooks, imagens, atas
>   ou qualquer outro material. Para isso, use `docs/`, `reports/` etc.
> - **Não** crie aqui arquivos específicos de uma ferramenta. Eles ficam em `CLAUDE.md` /
>   `.claude/` (Claude) e em `.github/copilot-instructions.md` / `.github/instructions/` /
>   `.github/prompts/` (Copilot).
> - Tudo o que está aqui é lido pelas duas IAs. Mudar um arquivo daqui muda o
>   comportamento de ambas.

Quem consome esta pasta:

- **Claude Code**: via `CLAUDE.md` na raiz, que importa estes arquivos com `@`.
- **GitHub Copilot (VS Code)**: via `.github/copilot-instructions.md` e
  `.github/instructions/*.instructions.md`, que referenciam estes arquivos.

| Arquivo | Conteúdo | Pode mudar? |
|---|---|---|
| [00-tech-challenge.md](00-tech-challenge.md) | Enunciado oficial transcrito (**fonte da verdade**) | Não, só correções de transcrição |
| [01-arquitetura.md](01-arquitetura.md) | Pipeline, estrutura de pastas, decisões técnicas | Sim, registre as decisões |
| [02-convencoes.md](02-convencoes.md) | Código, testes, commits, branches, regras de IA | Sim, com acordo do grupo |
| [03-checklist-entregaveis.md](03-checklist-entregaveis.md) | Checklist de requisitos × critérios de avaliação | Sim, marque o progresso |
| [04-governanca-lgpd.md](04-governanca-lgpd.md) | Guia para a seção de Governança/LGPD do README | Sim |
| [05-interfaces.md](05-interfaces.md) | Formatos dos artefatos trocados entre as trilhas (trabalho assíncrono) | Só via PR com o OK das trilhas afetadas |

**Regra de ouro:** ao mudar uma decisão, edite aqui e, se for algo central, atualize
também o resumo em `CLAUDE.md` e em `.github/copilot-instructions.md`.
