"""Schemas Pandera do contrato de dados.

Requisito do enunciado: pelo menos 3 regras RÍGIDAS. Regras planejadas:
  1. person_age entre MIN_AGE e MAX_AGE (idade ≥ 18)
  2. person_income não nula e entre MIN_INCOME e MAX_INCOME
  3. sem linhas duplicadas
  4. loan_status ∈ {0, 1} (apenas no schema de treino)
  5. categóricas dentro do domínio conhecido (loan_grade, loan_intent, ...)
"""

from __future__ import annotations

from typing import Any


def build_training_schema() -> Any:
    """Schema da Referência (features + target).

    TODO(T1.4): implementar com `import pandera.pandas as pa` (API do pandera ≥ 0.24),
    via DataFrameSchema ou DataFrameModel, com strict=True e checagem de duplicatas no
    nível do DataFrame.
    """
    raise NotImplementedError("T1.4")


def build_inference_schema() -> Any:
    """Schema dos lotes de produção (só features, sem target).

    TODO(T1.4): reaproveitar as regras do schema de treino, sem a coluna target.
    """
    raise NotImplementedError("T1.4")
