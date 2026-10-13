"""Métricas de saúde do modelo por janela (documentadas no README, T3.6)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def compute_health(
    predictions: pd.DataFrame,
    validation_log: pd.DataFrame,
    drift_results: dict[str, Any],
) -> pd.DataFrame:
    """Uma linha por janela com as métricas de saúde.

    TODO(T3.2): volume; % de predições nulas/erro; % de lotes bloqueados pelo contrato;
    latência p50/p95; taxa de aprovação e score médio; nº e share de features com drift;
    AUC/KS quando houver rótulo.
    """
    raise NotImplementedError("T3.2")
