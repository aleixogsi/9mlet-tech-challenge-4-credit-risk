"""Treino do baseline usando EXCLUSIVAMENTE o dataset de Referência."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def split_reference(reference: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa a Referência em treino e validação (holdout estratificado pelo target).

    Única definição do holdout: o treino do baseline e o relatório de vieses usam a mesma
    divisão, então as métricas de fairness são medidas em dados que o modelo não viu.
    """
    from sklearn.model_selection import train_test_split

    from credit_risk import config

    train, valid = train_test_split(
        reference,
        test_size=config.VALIDATION_FRACTION,
        random_state=config.SEED,
        stratify=reference[config.TARGET],
    )
    return train, valid


def train_baseline(reference: pd.DataFrame) -> Any:
    """Treina o pipeline na Referência (já validada pelo contrato) e devolve o modelo.

    A coluna de identificação nunca entra no modelo.
    """
    from credit_risk import config
    from credit_risk.training.pipeline import build_pipeline

    model = build_pipeline(config.NUMERIC_FEATURES, config.CATEGORICAL_FEATURES, config.SEED)
    model.fit(reference[config.FEATURES], reference[config.TARGET])
    return model
