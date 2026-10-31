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

import pandera.pandas as pa


def build_training_schema() -> Any:
    """Schema da Referência (features + target).

    O schema é estrito para impedir colunas desconhecidas.
    """
    return _build_schema(include_target=True)


def build_inference_schema() -> Any:
    """Schema dos lotes de produção (só features, sem target).

    O schema de inferência mantém o identificador interno, mas não aceita target.
    """
    return _build_schema(include_target=False)


def _build_schema(include_target: bool) -> pa.DataFrameSchema:
    from credit_risk import config

    columns: dict[str, pa.Column] = {
        config.ID_COLUMN: pa.Column(str, nullable=False, unique=True),
        "person_age": pa.Column(
            float, checks=pa.Check.between(config.MIN_AGE, config.MAX_AGE), nullable=False
        ),
        "person_income": pa.Column(
            float,
            checks=pa.Check.between(config.MIN_INCOME, config.MAX_INCOME),
            nullable=False,
        ),
        "person_emp_length": pa.Column(float, nullable=False),
        "loan_amnt": pa.Column(float, checks=pa.Check.ge(0), nullable=False),
        "loan_int_rate": pa.Column(float, checks=pa.Check.ge(0), nullable=False),
        "loan_percent_income": pa.Column(float, checks=pa.Check.ge(0), nullable=False),
        "cb_person_cred_hist_length": pa.Column(
            float, checks=pa.Check.ge(0), nullable=False
        ),
        "person_home_ownership": pa.Column(
            str, checks=pa.Check.isin(["RENT", "OWN", "MORTGAGE", "OTHER"]), nullable=False
        ),
        "loan_intent": pa.Column(
            str,
            checks=pa.Check.isin(
                [
                    "PERSONAL",
                    "EDUCATION",
                    "MEDICAL",
                    "VENTURE",
                    "HOMEIMPROVEMENT",
                    "DEBTCONSOLIDATION",
                ]
            ),
            nullable=False,
        ),
        "loan_grade": pa.Column(
            str, checks=pa.Check.isin(["A", "B", "C", "D", "E", "F", "G"]), nullable=False
        ),
        "cb_person_default_on_file": pa.Column(
            str, checks=pa.Check.isin(["Y", "N"]), nullable=False
        ),
    }
    if include_target:
        columns[config.TARGET] = pa.Column(
            int, checks=pa.Check.isin([0, 1]), nullable=False
        )
    return pa.DataFrameSchema(
        columns,
        checks=[
            pa.Check(
                lambda frame: not frame.duplicated().any(),
                name="no_duplicate_rows",
            )
        ],
        strict=True,
        coerce=True,
    )
