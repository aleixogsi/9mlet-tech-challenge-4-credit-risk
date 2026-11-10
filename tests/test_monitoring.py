"""Testes de observabilidade (Etapa 3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from credit_risk.inference import PREDICTION_FIELDS

MOCKS_DIR = Path(__file__).parent / "fixtures" / "mocks"
VALIDATION_FIELDS = ("timestamp", "batch_name", "rows", "status", "n_failures", "failed_rules")
DRIFT_WINDOW_FIELDS = (
    "window",
    "rows",
    "n_features",
    "n_drifted",
    "share_drifted",
    "features",
    "prediction_drift",
    "performance",
    "report_html",
)


def test_mock_predictions_follow_frozen_interface() -> None:
    """Mocks de predictions.jsonl seguem a interface congelada (T3.0)."""
    path = MOCKS_DIR / "predictions.jsonl"
    assert path.exists()
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(records) > 0
    for record in records:
        assert tuple(record.keys()) == PREDICTION_FIELDS
        assert record["decision"] in {"approved", "denied", "error"}
        assert len(record["record_id"]) == 64


def test_mock_validation_follows_frozen_interface() -> None:
    """Mocks de validation.jsonl seguem a interface congelada (T3.0)."""
    path = MOCKS_DIR / "validation.jsonl"
    assert path.exists()
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(records) > 0
    for record in records:
        assert tuple(record.keys()) == VALIDATION_FIELDS
        assert record["status"] in {"passed", "blocked"}


def test_mock_drift_summary_follows_frozen_interface() -> None:
    """Mock de drift_summary.json segue a interface congelada (T3.0)."""
    path = MOCKS_DIR / "drift_summary.json"
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert {"generated_at", "reference_rows", "windows"} <= set(payload.keys())
    assert [w["window"] for w in payload["windows"]] == ["t1", "t2", "t3", "t4", "t5"]
    for window in payload["windows"]:
        assert tuple(window.keys()) == DRIFT_WINDOW_FIELDS


@pytest.mark.skip(reason="TODO(T3.1): implementar após prediction_logger")
def test_prediction_log_has_no_pii() -> None:
    """O log só contém os campos do formato documentado em prediction_logger.py."""


@pytest.mark.skip(reason="TODO(T3.2): implementar após compute_health")
def test_health_metrics_per_window() -> None:
    """compute_health devolve uma linha por janela com as métricas esperadas."""


@pytest.mark.skip(reason="TODO(T3.3): implementar após evaluate_alerts")
def test_drift_alert_fires_above_threshold() -> None:
    """Share de features com drift ≥ ALERT_DRIFT_SHARE → alerta data_drift."""
