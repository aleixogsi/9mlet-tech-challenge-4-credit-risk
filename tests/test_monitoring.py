"""Testes de observabilidade (Etapa 3). Implementar em T3.2/T3.3."""

import pytest

pytestmark = pytest.mark.skip(reason="TODO(T3.2/T3.3): implementar após health e alerts")


def test_prediction_log_has_no_pii() -> None:
    """O log só contém os campos do formato documentado em prediction_logger.py."""


def test_health_metrics_per_window() -> None:
    """compute_health devolve uma linha por janela com as métricas esperadas."""


def test_drift_alert_fires_above_threshold() -> None:
    """Share de features com drift ≥ ALERT_DRIFT_SHARE → alerta data_drift."""
