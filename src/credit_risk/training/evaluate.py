"""Métricas de performance do modelo (baseline e janelas de produção com rótulo)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def evaluate(model: Any, X: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    """Retorna AUC, KS, Gini, F1, precisão e recall.

    TODO(T1.9): também é usada na Etapa 2/3 para evidenciar a queda de performance
    (concept drift) nas janelas de produção.
    """
    raise NotImplementedError("T1.9")


def feature_importance(model: Any) -> pd.DataFrame:
    """Importância das features, usada para escolher quais variáveis sofrerão drift (T2.1).

    TODO(T1.9)
    """
    raise NotImplementedError("T1.9")
