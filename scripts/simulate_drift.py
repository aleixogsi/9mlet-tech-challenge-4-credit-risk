"""Etapa 2: gera as janelas de produção (t1..tN) com drift, a partir do YAML de cenários.

Uso: uv run python scripts/simulate_drift.py
"""

from __future__ import annotations

import logging

import pandas as pd

from credit_risk import config
from credit_risk.drift.scenarios import build_windows, load_scenarios

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Cenários: %s", config.DRIFT_SCENARIOS_FILE)
    scenarios = load_scenarios(config.DRIFT_SCENARIOS_FILE)
    production_base = pd.read_parquet(config.PRODUCTION_BASE_FILE)
    windows = build_windows(production_base, scenarios)
    config.PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in windows.items():
        path = config.PRODUCTION_DIR / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        logger.info(
            "%s: %d linhas | default %.1f%% | renda média %.0f | juros médio %.2f → %s",
            name,
            len(frame),
            100 * frame[config.TARGET].mean(),
            frame["person_income"].mean(),
            frame["loan_int_rate"].mean(),
            path,
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
