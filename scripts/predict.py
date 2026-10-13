"""Etapas 2 e 3: para cada janela, valida pelo contrato → prediz → grava o log de predições.

Lotes que violam o contrato são BLOQUEADOS (não são preditos) e o bloqueio é logado.

Uso: uv run python scripts/predict.py [--window t3]
"""

from __future__ import annotations

import argparse
import logging

from credit_risk import config

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", help="Janela específica (padrão: todas)")
    args = parser.parse_args()
    logger.info("Modelo: %s | janela: %s", config.MODEL_FILE, args.window or "todas")
    # TODO(T2.4): carregar o modelo; para cada janela: validate_or_block (schema de inferência)
    # → predict_proba com medição de latência → log_predictions (sem PII) em PREDICTIONS_LOG
    raise NotImplementedError("T2.4")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
