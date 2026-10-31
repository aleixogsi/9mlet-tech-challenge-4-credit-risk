"""Análise de vieses do modelo por grupo (evidência para a seção de vieses do README)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def fairness_by_group(model: Any, df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Métricas por grupo: volume, aprovação, default real, AUC e taxa de falso negativo.

    TODO(T4.3): grupos sugeridos: faixa etária (derivada de person_age) e
    person_home_ownership. Destacar diferenças grandes entre os grupos (ex.: razão
    entre as taxas de aprovação < 0.8).
    """
    raise NotImplementedError("T4.3")
