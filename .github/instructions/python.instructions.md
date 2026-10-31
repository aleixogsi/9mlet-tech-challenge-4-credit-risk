---
applyTo: "**/*.py"
description: Convenções de Python do projeto
---

# Código Python

Siga [context/02-convencoes.md](../../context/02-convencoes.md).

- Python 3.11+, type hints em funções públicas, formatação/lint com `ruff`.
- Nomes em inglês. Docstrings consistentes dentro do módulo.
- Módulos de `src/credit_risk/` sem I/O escondido: leitura e gravação de arquivos ficam
  em `scripts/` ou em funções de borda explícitas.
- Use `logging`, não `print`, em `src/`.
- Caminhos, seeds e thresholds (PSI, KS, alertas) vêm de `src/credit_risk/config.py`.
- Toda aleatoriedade com seed (`random_state`, `np.random.default_rng(seed)`).
- Nunca logar PII. Use IDs pseudonimizados.
- Toda função nova em `src/` deve ter teste correspondente em `tests/`.
