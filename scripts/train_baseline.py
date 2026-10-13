"""Etapa 1: treina o baseline na Referência e salva o modelo e as métricas.

Uso: uv run python scripts/train_baseline.py
"""

from __future__ import annotations

import logging

from credit_risk import config

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Treinando %s com %s", config.MODEL_VERSION, config.REFERENCE_FILE)
    # TODO(T1.8/T1.9): validar a Referência pelo contrato → train_baseline → evaluate →
    # salvar MODEL_FILE, reports/training/metrics.json e feature_importance.csv
    raise NotImplementedError("T1.8")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
