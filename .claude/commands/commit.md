---
description: Cria commit(s) semântico(s) em pt-BR seguindo as convenções do projeto
argument-hint: "[dica opcional sobre o escopo]"
---

Crie commits seguindo `context/02-convencoes.md` (seção Git).

1. Rode `git status` e `git diff` (inclusive o staged) para entender as mudanças.
2. Verifique se **nada proibido** está sendo commitado: `data/`, `.env`, arquivos com
   PII, modelos grandes. Se houver, pare e avise.
3. Agrupe as mudanças em **commits lógicos** (um commit por mudança coerente). Se as
   mudanças misturarem assuntos, proponha a divisão.
4. Mensagem no formato `<tipo>(<escopo>): <descrição>`, em pt-BR, no imperativo,
   minúscula, sem ponto final. Use o corpo para explicar o *porquê*, quando não for óbvio.
   Escopos: `contracts`, `training`, `drift`, `monitoring`, `governance`, `data`, `context`.
5. Mostre as mensagens propostas e só então faça os commits. **Não faça push.**

Dica do usuário: $ARGUMENTS
