"""Testes de observabilidade (Etapa 3)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from credit_risk.inference import PREDICTION_FIELDS, build_prediction_records
from credit_risk.monitoring.prediction_logger import log_predictions, read_predictions

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


def test_prediction_log_has_no_pii(tmp_path: Path) -> None:
    """O log só contém os campos do formato documentado em prediction_logger.py (T3.1)."""
    ids = pd.Series(["application_00000001", "application_00000002"])
    records = build_prediction_records(
        ids=ids,
        scores=np.array([0.15, np.nan]),
        latencies_ms=np.array([2.5, 3.1]),
        window="t1",
        salt="test-salt",
        timestamp="2026-11-01T12:00:00Z",
    )
    log_path = tmp_path / "predictions.jsonl"
    written = log_predictions(records, log_path)
    assert written == 2

    df = read_predictions(log_path)
    assert list(df.columns) == list(PREDICTION_FIELDS)
    assert len(df) == 2
    assert df.loc[0, "decision"] == "approved"
    assert pd.isna(df.loc[1, "score"])
    assert df.loc[1, "decision"] == "error"
    assert "application_0000000" not in log_path.read_text(encoding="utf-8")


def test_prediction_logger_rejects_pii_or_extra_fields(tmp_path: Path) -> None:
    """Qualquer campo extra (ex.: application_id ou cpf) ou ID não-hash é bloqueado."""
    ids = pd.Series(["application_00000001"])
    valid_record = build_prediction_records(
        ids=ids,
        scores=np.array([0.25]),
        latencies_ms=np.array([1.8]),
        window="t1",
        salt="test-salt",
        timestamp="2026-11-01T12:00:00Z",
    )[0]

    with_extra = {**valid_record, "application_id": "application_00000001"}
    with pytest.raises(ValueError, match="Registro de predição inválido"):
        log_predictions([with_extra], tmp_path / "extra.jsonl")

    with_raw_id = {**valid_record, "record_id": "application_00000001"}
    with pytest.raises(ValueError, match="SHA-256"):
        log_predictions([with_raw_id], tmp_path / "raw_id.jsonl")


def test_read_predictions_handles_mock_and_missing_file(tmp_path: Path) -> None:
    """read_predictions carrega o mock de T3.0 e falha se o arquivo não existir."""
    df = read_predictions(MOCKS_DIR / "predictions.jsonl")
    assert len(df) == 15
    assert set(df["window"].unique()) == {"t1", "t2", "t3", "t4", "t5"}

    with pytest.raises(FileNotFoundError):
        read_predictions(tmp_path / "inexistente.jsonl")


@pytest.mark.skip(reason="TODO(T3.2): implementar após compute_health")
def test_health_metrics_per_window() -> None:
    """compute_health devolve uma linha por janela com as métricas esperadas."""


@pytest.mark.skip(reason="TODO(T3.3): implementar após evaluate_alerts")
def test_drift_alert_fires_above_threshold() -> None:
    """Share de features com drift ≥ ALERT_DRIFT_SHARE → alerta data_drift."""
