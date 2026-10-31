"""Separação física entre dataset de Referência (treino) e base de Produção."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def split_reference_production(
    df: pd.DataFrame, reference_fraction: float, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Divide a base limpa em (referência, base_de_produção).

    A base de produção é o ponto de partida das janelas com drift (Etapa 2) e
    **nunca** é usada no treino.

    A divisão é estratificada para preservar a taxa de default nos dois conjuntos.
    """
    from sklearn.model_selection import train_test_split

    if not 0 < reference_fraction < 1:
        raise ValueError("reference_fraction deve estar entre 0 e 1")
    reference, production = train_test_split(
        df,
        train_size=reference_fraction,
        random_state=seed,
        stratify=df["loan_status"],
    )
    return reference.reset_index(drop=True), production.reset_index(drop=True)
