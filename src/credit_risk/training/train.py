"""Treino do baseline usando EXCLUSIVAMENTE o dataset de Referência."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def train_baseline(reference: pd.DataFrame) -> Any:
    """Treina o pipeline na Referência (já validada pelo contrato) e devolve o modelo.

    TODO(T1.8): split treino/validação interno, fit e retorno do pipeline treinado.
    """
    raise NotImplementedError("T1.8")
