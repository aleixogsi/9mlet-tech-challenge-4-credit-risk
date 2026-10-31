"""Geração do lote com erros usado para demonstrar o contrato bloqueando a ingestão."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def make_bad_batch(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Copia uma amostra válida e injeta pelo menos uma violação de CADA regra rígida.

    Injeta idade inválida, renda nula, categoria inválida, target inválido e duplicata.
    """
    from credit_risk import config

    if len(df) < 5:
        raise ValueError("São necessárias ao menos cinco linhas para gerar o lote ruim")
    result = df.sample(frac=1, random_state=seed).reset_index(drop=True).copy()
    result.loc[0, "person_age"] = config.MIN_AGE - 1
    result.loc[1, "person_income"] = None
    result.loc[2, "loan_intent"] = "UNKNOWN"
    result.loc[3, config.TARGET] = 2
    result.loc[4] = result.loc[0]
    return result
