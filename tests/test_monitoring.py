"""Testes de observabilidade (Etapa 3)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from credit_risk.inference import PREDICTION_FIELDS, build_prediction_records
from credit_risk.monitoring.alerts import (
    ALERT_FIELDS,
    ALERT_SEVERITIES,
    ALERT_TYPES,
    evaluate_alerts,
    write_alerts,
)
from credit_risk.monitoring.dashboard import build_dashboard
from credit_risk.monitoring.health import (
    HEALTH_COLUMNS,
    compute_health,
    read_drift_summary,
    read_validation_log,
)
from credit_risk.monitoring.prediction_logger import log_predictions, read_predictions
from credit_risk.monitoring.prometheus_exporter import (
    render_prometheus_metrics,
    write_prometheus_metrics,
)
from credit_risk.monitoring.server import create_observability_server

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


def test_health_metrics_per_window() -> None:
    """compute_health devolve uma linha por janela com as métricas esperadas (T3.2)."""
    predictions = read_predictions(MOCKS_DIR / "predictions.jsonl")
    validation_log = read_validation_log(MOCKS_DIR / "validation.jsonl")
    drift_results = read_drift_summary(MOCKS_DIR / "drift_summary.json")

    health = compute_health(predictions, validation_log, drift_results)
    assert list(health.columns) == HEALTH_COLUMNS
    assert list(health["window"]) == ["t1", "t2", "t3", "t4", "t5"]
    assert (health["volume"] == 3).all()

    t1 = health.loc[health["window"] == "t1"].iloc[0]
    assert t1["null_predictions_pct"] == 0.0
    assert t1["blocked_batches_pct"] == 0.0
    assert pytest.approx(t1["approval_rate"], rel=1e-4) == 2 / 3
    assert t1["share_drifted"] == 0.0
    assert t1["drifted_features"] == []

    t4 = health.loc[health["window"] == "t4"].iloc[0]
    assert pytest.approx(t4["null_predictions_pct"], rel=1e-4) == 1 / 3
    assert t4["n_batches"] == 2
    assert t4["n_blocked_batches"] == 1
    assert t4["blocked_batches_pct"] == 0.5
    assert t4["n_drifted"] == 4
    assert t4["share_drifted"] == 0.3636
    assert "loan_int_rate" in t4["drifted_features"]
    assert t4["auc_drop"] > 0.05

    t5 = health.loc[health["window"] == "t5"].iloc[0]
    assert t5["latency_p95_ms"] > 200.0
    assert pytest.approx(t5["gini"], rel=1e-4) == 2 * t5["auc"] - 1
    assert len(health.attrs["extra_blocked_batches"]) == 1
    assert health.attrs["extra_blocked_batches"][0]["batch_name"] == "bad_batch"


def test_drift_alert_fires_above_threshold() -> None:
    """Share de features com drift ≥ ALERT_DRIFT_SHARE → alerta data_drift (T3.3)."""
    predictions = read_predictions(MOCKS_DIR / "predictions.jsonl")
    validation_log = read_validation_log(MOCKS_DIR / "validation.jsonl")
    drift_results = read_drift_summary(MOCKS_DIR / "drift_summary.json")

    health = compute_health(predictions, validation_log, drift_results)
    alerts = evaluate_alerts(health)

    data_drift_windows = [a["window"] for a in alerts if a["type"] == "data_drift"]
    assert data_drift_windows == ["t4", "t5"]


def test_all_alert_types_and_write_alerts(tmp_path: Path) -> None:
    """Todos os 6 tipos de alerta são avaliados e gravados em alerts.jsonl (T3.3)."""
    predictions = read_predictions(MOCKS_DIR / "predictions.jsonl")
    validation_log = read_validation_log(MOCKS_DIR / "validation.jsonl")
    drift_results = read_drift_summary(MOCKS_DIR / "drift_summary.json")

    health = compute_health(predictions, validation_log, drift_results)
    alerts = evaluate_alerts(health)

    fired_types = {a["type"] for a in alerts}
    assert fired_types == ALERT_TYPES
    for alert in alerts:
        assert tuple(alert.keys()) == ALERT_FIELDS
        assert alert["severity"] in ALERT_SEVERITIES

    alerts_path = tmp_path / "alerts.jsonl"
    write_alerts(alerts, alerts_path)
    loaded = [json.loads(line) for line in alerts_path.read_text(encoding="utf-8").splitlines()]
    assert len(loaded) == len(alerts)
    assert tuple(loaded[0].keys()) == ALERT_FIELDS


def test_build_dashboard_renders_health_alerts_and_links(tmp_path: Path) -> None:
    """build_dashboard gera o HTML com as 3 seções obrigatórias e links (T3.4)."""
    predictions = read_predictions(MOCKS_DIR / "predictions.jsonl")
    validation_log = read_validation_log(MOCKS_DIR / "validation.jsonl")
    drift_results = read_drift_summary(MOCKS_DIR / "drift_summary.json")

    health = compute_health(predictions, validation_log, drift_results)
    alerts = evaluate_alerts(health)
    output_html = tmp_path / "monitoring" / "index.html"

    result_path = build_dashboard(health, alerts, output_html)
    assert result_path == output_html
    assert output_html.exists()

    html_content = output_html.read_text(encoding="utf-8")
    assert "1. Métricas de Saúde por Janela" in html_content
    assert "2. Alertas de Degradação e Qualidade" in html_content
    assert "3. Relatórios Evidently e Evidências de Auditoria" in html_content
    for win in ["t1", "t2", "t3", "t4", "t5"]:
        assert f"../drift/drift_{win}.html" in html_content
        assert f"../drift/performance_{win}.html" in html_content
    assert "../validation/bad_batch_failures.csv" in html_content
    assert "cell-critical" in html_content
    assert "badge-critical" in html_content


def test_monitor_script_end_to_end(tmp_path: Path) -> None:
    """scripts/monitor.py lê os artefatos, grava alerts.jsonl e gera index.html (T3.5)."""
    import importlib.util

    script_path = Path(__file__).parents[1] / "scripts" / "monitor.py"
    spec = importlib.util.spec_from_file_location("monitor_script", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    alerts_out = tmp_path / "logs" / "alerts.jsonl"
    html_out = tmp_path / "reports" / "monitoring" / "index.html"
    prom_out = tmp_path / "reports" / "monitoring" / "metrics.prom"

    result = module.run_monitoring(
        predictions_path=MOCKS_DIR / "predictions.jsonl",
        validation_path=MOCKS_DIR / "validation.jsonl",
        drift_summary_path=MOCKS_DIR / "drift_summary.json",
        alerts_path=alerts_out,
        output_html=html_out,
        output_prom=prom_out,
    )
    assert result == html_out
    assert html_out.exists()
    assert prom_out.exists()
    assert alerts_out.exists()
    lines = [json.loads(line) for line in alerts_out.read_text(encoding="utf-8").splitlines()]
    assert len(lines) > 0


def test_prometheus_exporter_generates_metrics(tmp_path: Path) -> None:
    """Exportador Prometheus gera gauges credit_risk_* por janela e alertas (T3.7)."""
    predictions = read_predictions(MOCKS_DIR / "predictions.jsonl")
    validation_log = read_validation_log(MOCKS_DIR / "validation.jsonl")
    drift_results = read_drift_summary(MOCKS_DIR / "drift_summary.json")

    health = compute_health(predictions, validation_log, drift_results)
    alerts = evaluate_alerts(health)

    payload = render_prometheus_metrics(health, alerts)
    assert 'credit_risk_share_drifted{window="t5"} 0.3636' in payload
    assert 'credit_risk_auc{window="t1"} 0.924' in payload
    assert 'credit_risk_alerts_total{severity="critical",type="data_drift",window="t4"}' in payload

    prom_file = tmp_path / "metrics.prom"
    write_prometheus_metrics(health, alerts, prom_file)
    assert prom_file.exists()
    assert "credit_risk_prediction_psi" in prom_file.read_text(encoding="utf-8")


def test_observability_server_endpoints(tmp_path: Path) -> None:
    """Servidor HTTP unificado responde em /, /monitoring/index.html, /metrics e /api/*."""
    import threading
    from urllib.request import urlopen

    predictions = read_predictions(MOCKS_DIR / "predictions.jsonl")
    validation_log = read_validation_log(MOCKS_DIR / "validation.jsonl")
    drift_results = read_drift_summary(MOCKS_DIR / "drift_summary.json")

    health = compute_health(predictions, validation_log, drift_results)
    alerts = evaluate_alerts(health)
    build_dashboard(health, alerts, tmp_path / "monitoring" / "index.html")

    server = create_observability_server(
        health=health,
        alerts=alerts,
        reports_dir=tmp_path,
        host="127.0.0.1",
        port=0,
    )
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{port}/") as resp:
            body = resp.read().decode("utf-8")
            assert "1. Métricas de Saúde por Janela" in body

        with urlopen(f"http://127.0.0.1:{port}/metrics") as resp:
            metrics_body = resp.read().decode("utf-8")
            assert "credit_risk_share_drifted" in metrics_body

        with urlopen(f"http://127.0.0.1:{port}/api/health") as resp:
            health_json = json.loads(resp.read().decode("utf-8"))
            assert len(health_json) == 5

        with urlopen(f"http://127.0.0.1:{port}/api/alerts") as resp:
            alerts_json = json.loads(resp.read().decode("utf-8"))
            assert len(alerts_json) == len(alerts)
    finally:
        server.shutdown()
        server.server_close()
