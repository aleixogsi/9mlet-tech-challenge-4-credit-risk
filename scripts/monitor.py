"""Etapa 3: consolida logs + resultados de drift → métricas de saúde, alertas e painel.

Uso: uv run python scripts/monitor.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from credit_risk import config
from credit_risk.monitoring.alerts import evaluate_alerts, write_alerts
from credit_risk.monitoring.dashboard import build_dashboard
from credit_risk.monitoring.health import (
    compute_health,
    read_drift_summary,
    read_validation_log,
)
from credit_risk.monitoring.prediction_logger import read_predictions

logger = logging.getLogger(__name__)


def run_monitoring(
    predictions_path: Path | None = None,
    validation_path: Path | None = None,
    drift_summary_path: Path | None = None,
    alerts_path: Path | None = None,
    output_html: Path | None = None,
) -> Path:
    """Executa o fluxo de observabilidade de ponta a ponta e devolve o caminho do painel HTML."""
    pred_file = predictions_path or config.PREDICTIONS_LOG
    val_file = validation_path or config.VALIDATION_LOG
    drift_file = drift_summary_path or (config.DRIFT_REPORTS_DIR / "drift_summary.json")
    alert_file = alerts_path or config.ALERTS_LOG
    html_file = output_html or (config.MONITORING_REPORTS_DIR / "index.html")

    predictions = read_predictions(pred_file)
    validation_log = read_validation_log(val_file)
    drift_results = read_drift_summary(drift_file)

    health = compute_health(predictions, validation_log, drift_results)
    alerts = evaluate_alerts(health)

    if alert_file.exists():
        alert_file.unlink()
    write_alerts(alerts, alert_file)

    dashboard_path = build_dashboard(health, alerts, html_file)
    n_crit = sum(1 for a in alerts if a.get("severity") == "critical")
    n_warn = sum(1 for a in alerts if a.get("severity") == "warning")
    logger.info(
        "Monitoramento concluído: %d janelas | %d alertas (%d critical, %d warning) | painel: %s",
        len(health),
        len(alerts),
        n_crit,
        n_warn,
        dashboard_path,
    )
    return dashboard_path


def main() -> int:
    run_monitoring()
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    sys.exit(main())
