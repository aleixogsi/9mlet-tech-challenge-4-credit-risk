---
applyTo: "src/credit_risk/contracts/**,src/credit_risk/data/**,scripts/validate_data.py,tests/**/test_contract*.py"
description: Regras para contratos de dados (Etapa 1, 25% da nota)
---

# Contratos de dados (Etapa 1)

Requisitos do enunciado ([00-tech-challenge.md](../../context/00-tech-challenge.md)):

- Use **Pandera** ou **Great Expectations** (a escolhida está no registro de decisões de
  `01-arquitetura.md`). Não use validação manual com `if`/`assert` no lugar da lib.
- **Pelo menos 3 regras rígidas**. Ex.: idade ≥ 18, renda não nula e > 0, sem duplicatas,
  target ∈ {0, 1}, domínios de categóricas.
- A validação **bloqueia a ingestão**: dados inválidos levantam exceção (ex.:
  `SchemaErrors` com `lazy=True`, para listar todas as falhas) e o script sai com
  exit code ≠ 0. Os dados não seguem para predição.
- Registre a falha (quais regras, quantas linhas) em log ou relatório, para evidenciar a
  demonstração.
- Deve existir um **lote com erros** reproduzível (em `data/bad_batches/` ou gerado por
  script) que viola cada regra rígida.
- Testes: o dataset válido passa, e cada regra falha isoladamente com o lote ruim
  correspondente.
- Referência e Produção ficam sempre separados (arquivos/pastas distintos).
