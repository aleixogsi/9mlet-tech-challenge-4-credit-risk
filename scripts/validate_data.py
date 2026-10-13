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

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", help="Arquivo parquet/csv do lote")
    parser.add_argument("--schema", choices=["training", "inference"], default="inference")
    parser.add_argument("--make-bad-batch", action="store_true", help="Gera o lote com erros")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger.info("Lote: %s | schema: %s", args.path, args.schema)
    # TODO(T1.5/T1.6): carregar o lote, validate_or_block; em DataContractError,
    # write_validation_report e return 1. Com --make-bad-batch, gerar config.BAD_BATCH_FILE.
    raise NotImplementedError("T1.5")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    sys.exit(main())
