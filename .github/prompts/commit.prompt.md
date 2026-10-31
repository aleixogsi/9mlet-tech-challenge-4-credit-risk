---
description: Cria commit(s) semântico(s) em pt-BR seguindo as convenções do projeto
---

Crie commits seguindo [02-convencoes.md](../../context/02-convencoes.md) (seção Git).

1. Analise as mudanças (`git status` e `git diff`, inclusive o staged).
2. Verifique se **nada proibido** está sendo commitado: `data/`, `.env`, arquivos com
   PII, modelos grandes. Se houver, pare e avise.
3. Agrupe as mudanças em **commits lógicos** (um commit por mudança coerente).
4. Mensagem no formato `<tipo>(<escopo>): <descrição>`, em pt-BR, no imperativo,
   minúscula, sem ponto final. Use o corpo para explicar o *porquê*, quando não for óbvio.
   Escopos: `contracts`, `training`, `drift`, `monitoring`, `governance`, `data`, `context`.
5. Mostre as mensagens propostas antes de commitar. **Não faça push.**

${input:dica:Dica opcional sobre o escopo}
