"""Etapa 1: dados brutos → Referência (data/reference) + base de Produção (data/production).

Uso: uv run python scripts/prepare_data.py
"""

from __future__ import annotations

import logging

from credit_risk import config
from credit_risk.data.clean import clean
from credit_risk.data.load import load_raw
from credit_risk.data.privacy import minimize_columns
from credit_risk.data.split import split_reference_production

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Lendo %s", config.RAW_DATASET_FILE)
    frame = load_raw(config.RAW_DATASET_FILE)
    frame = minimize_columns(frame, [config.ID_COLUMN, *config.FEATURES, config.TARGET])
    cleaned = clean(frame)
    reference, production = split_reference_production(
        cleaned, config.REFERENCE_FRACTION, config.SEED
    )
    config.REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    config.PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)
    reference.to_parquet(config.REFERENCE_FILE, index=False)
    production.to_parquet(config.PRODUCTION_BASE_FILE, index=False)
    logger.info("Referência: %d linhas | Produção: %d linhas", len(reference), len(production))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
