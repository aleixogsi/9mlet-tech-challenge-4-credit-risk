"""Regras de alerta sobre as métricas de saúde e de drift."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def evaluate_alerts(health: pd.DataFrame) -> list[dict[str, Any]]:
    """Compara as métricas com os thresholds ALERT_* de config.py.

    Cada alerta: {"window", "type", "metric", "value", "threshold", "severity", "message"}.

    TODO(T3.3): tipos mínimos: data_drift, prediction_drift, performance_drop,
    null_predictions, latency, contract_blocked.
    """
    raise NotImplementedError("T3.3")


def write_alerts(alerts: list[dict[str, Any]], path: Path) -> None:
    """Anexa os alertas em logs/alerts.jsonl.

    TODO(T3.3)
    """
    raise NotImplementedError("T3.3")
