"""Baixa e valida o Credit Risk Dataset no diretório esperado pelo pipeline.

Uso:
    uv run python scripts/download_data.py
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

import pandas as pd

from credit_risk import config

logger = logging.getLogger(__name__)


def find_dataset_file(download_dir: Path) -> Path:
    """Localiza o CSV do dataset baixado pelo KaggleHub."""
    candidates = sorted(download_dir.rglob("credit_risk_dataset.csv"))
    if not candidates:
        raise FileNotFoundError(
            f"credit_risk_dataset.csv não encontrado no download: {download_dir}"
        )
    if len(candidates) > 1:
        raise RuntimeError(f"Mais de um CSV do dataset encontrado: {candidates}")
    return candidates[0]


def validate_columns(path: Path) -> None:
    """Confirma que o arquivo baixado possui o contrato de colunas bruto."""
    frame = pd.read_csv(path, nrows=0)
    expected = set(config.FEATURES) | {config.TARGET}
    missing = sorted(expected - set(frame.columns))
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes no dataset: {missing}")


def download_dataset(output_path: Path = config.RAW_DATASET_FILE) -> Path:
    """Baixa a versão atual do dataset e copia o CSV validado para o projeto."""
    import kagglehub

    download_dir = Path(kagglehub.dataset_download(config.KAGGLE_DATASET_SLUG))
    source_path = find_dataset_file(download_dir)
    validate_columns(source_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, output_path)
    logger.info("Dataset salvo em %s", output_path)
    return output_path


def main() -> None:
    download_dataset()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
