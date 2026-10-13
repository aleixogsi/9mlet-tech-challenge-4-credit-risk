"""Etapa 3: consolida logs + resultados de drift → métricas de saúde, alertas e painel.

Uso: uv run python scripts/monitor.py
"""

from __future__ import annotations

import logging

from credit_risk import config

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Painel em %s", config.MONITORING_REPORTS_DIR / "index.html")
    # TODO(T3.2–T3.5): read_predictions + validation log + drift_summary.json →
    # compute_health → evaluate_alerts/write_alerts → build_dashboard
    raise NotImplementedError("T3.5")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
