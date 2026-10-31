"""Leitura do dataset bruto (data/raw)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def load_raw(path: Path) -> pd.DataFrame:
    """Lê o CSV bruto do Credit Risk Dataset.

    O identificador interno é criado nesta borda e não depende de dados pessoais.
    """
    import pandas as pd

    from credit_risk import config

    if not path.exists():
        raise FileNotFoundError(f"Dataset bruto não encontrado: {path}")
    frame = pd.read_csv(path)
    expected = set(config.FEATURES) | {config.TARGET}
    missing = sorted(expected - set(frame.columns))
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes no dataset: {missing}")
    frame = frame[config.FEATURES + [config.TARGET]].copy()
    frame.insert(0, config.ID_COLUMN, [f"application_{i:08d}" for i in range(len(frame))])
    return frame
