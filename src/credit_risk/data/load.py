"""Leitura do dataset bruto (data/raw)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def load_raw(path: Path) -> pd.DataFrame:
    """Lê o CSV bruto do Credit Risk Dataset.

    TODO(T1.1): ler com tipos explícitos e validar se as colunas esperadas
    (config.FEATURES + config.TARGET) existem.
    """
    raise NotImplementedError("T1.1")
