"""Etapa 4: gera o relatório de vieses do modelo em reports/training/fairness.csv.

Uso: uv run python scripts/bias_report.py
"""

from __future__ import annotations

import logging

from credit_risk import config

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Relatório de vieses em %s", config.TRAINING_REPORTS_DIR / "fairness.csv")
    # TODO(T4.3): carregar o modelo e a Referência → fairness_by_group (faixa etária,
    # person_home_ownership) → salvar reports/training/fairness.csv
    raise NotImplementedError("T4.3")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
