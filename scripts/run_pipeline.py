"""Executa o projeto de ponta a ponta (roteiro da demo do vídeo STAR).

Uso: uv run python scripts/run_pipeline.py
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

from credit_risk import config

logger = logging.getLogger(__name__)

SCRIPTS_DIR = Path(__file__).resolve().parent

# (descrição, argumentos, deve_falhar)
STEPS: list[tuple[str, list[str], bool]] = [
    ("1. Preparar dados (Referência × Produção)", ["prepare_data.py"], False),
    (
        "1. Validar Referência",
        ["validate_data.py", "data/reference/reference.parquet", "--schema", "training"],
        False,
    ),
    ("1. Gerar e bloquear lote com erros", ["validate_data.py", "--make-bad-batch"], True),
    ("1. Treinar baseline", ["train_baseline.py"], False),
    ("4. Relatório de vieses", ["bias_report.py"], False),
    ("2. Simular drift", ["simulate_drift.py"], False),
    ("2. Predizer janelas de produção", ["predict.py"], False),
    ("2. Detectar drift", ["detect_drift.py"], False),
    ("3. Monitoramento", ["monitor.py"], False),
]


def clean_logs() -> None:
    """Remove logs anteriores para garantir uma execução limpa e determinística."""
    for log_file in (config.PREDICTIONS_LOG, config.VALIDATION_LOG, config.ALERTS_LOG):
        if log_file.exists():
            log_file.unlink()


def main() -> int:
    clean_logs()
    for description, args, should_fail in STEPS:
        logger.info("▶ %s", description)
        result = subprocess.run([sys.executable, str(SCRIPTS_DIR / args[0]), *args[1:]])
        failed = result.returncode != 0
        if failed != should_fail:
            logger.error("Etapa inesperada: %s (exit code %s)", description, result.returncode)
            return 1
    logger.info("Pipeline concluído. Veja reports/monitoring/index.html")
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    sys.exit(main())
