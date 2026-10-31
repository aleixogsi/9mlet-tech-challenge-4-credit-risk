"""Etapa 1: valida um lote contra o contrato. Sai com código 1 se o lote for BLOQUEADO.

Uso:
    uv run python scripts/validate_data.py data/reference/reference.parquet --schema training
    uv run python scripts/validate_data.py data/bad_batches/bad_batch.parquet   # deve falhar
    uv run python scripts/validate_data.py --make-bad-batch                     # gera o lote ruim
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from credit_risk import config
from credit_risk.contracts.bad_batch import make_bad_batch
from credit_risk.contracts.schemas import build_inference_schema, build_training_schema
from credit_risk.contracts.validator import (
    DataContractError,
    validate_or_block,
    write_validation_report,
)

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", help="Arquivo parquet/csv do lote")
    parser.add_argument("--schema", choices=["training", "inference"], default="inference")
    parser.add_argument("--make-bad-batch", action="store_true", help="Gera o lote com erros")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.make_bad_batch:
        source = pd.read_parquet(config.REFERENCE_FILE)
        batch = make_bad_batch(source, config.SEED)
        config.BAD_BATCHES_DIR.mkdir(parents=True, exist_ok=True)
        batch.to_parquet(config.BAD_BATCH_FILE, index=False)
        args.path = config.BAD_BATCH_FILE
        args.schema = "training"
    if args.path is None:
        raise ValueError("Informe um lote ou use --make-bad-batch")
    frame = pd.read_parquet(args.path) if args.path.suffix == ".parquet" else pd.read_csv(args.path)
    schema = build_training_schema() if args.schema == "training" else build_inference_schema()
    try:
        validate_or_block(frame, schema, args.path.stem)
    except DataContractError as error:
        write_validation_report(error.failures, args.path.stem, config.VALIDATION_REPORTS_DIR)
        logger.error("%s", error)
        return 1
    logger.info("Lote aprovado: %s", args.path)
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    sys.exit(main())
