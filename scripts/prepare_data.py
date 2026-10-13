"""Etapa 1: dados brutos → Referência (data/reference) + base de Produção (data/production).

Uso: uv run python scripts/prepare_data.py
"""

from __future__ import annotations

import logging

from credit_risk import config

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Lendo %s", config.RAW_DATASET_FILE)
    # TODO(T1.1/T1.2/T1.3): load_raw → minimize_columns → clean →
    # split_reference_production → salvar REFERENCE_FILE e PRODUCTION_BASE_FILE
    raise NotImplementedError("T1.2")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
