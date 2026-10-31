"""Treino do baseline usando EXCLUSIVAMENTE o dataset de Referência."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def train_baseline(reference: pd.DataFrame) -> Any:
    """Treina o pipeline na Referência (já validada pelo contrato) e devolve o modelo.

    A coluna de identificação nunca entra no modelo.
    """
    from credit_risk import config
    from credit_risk.training.pipeline import build_pipeline

    model = build_pipeline(config.NUMERIC_FEATURES, config.CATEGORICAL_FEATURES, config.SEED)
    model.fit(reference[config.FEATURES], reference[config.TARGET])
    return model
