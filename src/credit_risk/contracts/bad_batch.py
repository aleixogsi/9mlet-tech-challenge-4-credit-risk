"""Geração do lote com erros usado para demonstrar o contrato bloqueando a ingestão."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def make_bad_batch(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Copia uma amostra válida e injeta pelo menos uma violação de CADA regra rígida.

    TODO(T1.6): ex.: idade = 15, renda nula, renda negativa, linhas duplicadas,
    categoria desconhecida. Documente no docstring quais linhas violam quais regras.
    """
    raise NotImplementedError("T1.6")
