"""Etapa 2: gera as janelas de produção (t1..tN) com drift, a partir do YAML de cenários.

Uso: uv run python scripts/simulate_drift.py
"""

from __future__ import annotations

import logging

from credit_risk import config

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Cenários: %s", config.DRIFT_SCENARIOS_FILE)
    # TODO(T2.2/T2.3): load_scenarios → build_windows → salvar data/production/<janela>.parquet
    raise NotImplementedError("T2.3")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
