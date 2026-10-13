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

    TODO(T1.2): split estratificado pelo target, com seed fixa.
    """
    raise NotImplementedError("T1.2")
