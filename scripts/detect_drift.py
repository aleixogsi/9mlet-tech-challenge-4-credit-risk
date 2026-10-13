"""Etapa 2: compara Referência × cada janela de Produção (PSI/KS + Evidently).

Saídas em reports/drift/: drift_<janela>.html, performance_<janela>.html,
psi_ks_<janela>.csv e drift_summary.json (consumido pelo monitoramento).

Uso: uv run python scripts/detect_drift.py
"""

from __future__ import annotations

import logging

from credit_risk import config

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Relatórios em %s", config.DRIFT_REPORTS_DIR)
    # TODO(T2.6): por janela: build_drift_report (Evidently, PSI e KS) → drift_table →
    # build_performance_report → consolidar em reports/drift/drift_summary.json
    raise NotImplementedError("T2.6")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
