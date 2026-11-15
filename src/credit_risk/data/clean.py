"""Limpeza do dataset bruto para gerar a base limpa (origem da Referência)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove/corrige registros inválidos para que a Referência passe no contrato.

    Registros que não podem ser corrigidos sem inventar informação são removidos. As
    duplicatas são comparadas sem o `application_id`: o ID é criado em `load_raw`, antes da
    limpeza, então duas linhas iguais no CSV chegam aqui com IDs diferentes.
    """
    import logging

    from credit_risk import config

    logger = logging.getLogger(__name__)

    result = df.copy()
    before = len(result)
    content = [column for column in result.columns if column != config.ID_COLUMN]
    result = result.drop_duplicates(subset=content)
    logger.info("Limpeza: %d duplicatas removidas", before - len(result))

    before = len(result)
    result = result.dropna(subset=config.FEATURES + [config.TARGET])
    logger.info("Limpeza: %d linhas com nulos removidas", before - len(result))

    before = len(result)
    result = result[result["person_age"].between(config.MIN_AGE, config.MAX_AGE)]
    logger.info("Limpeza: %d linhas fora do limite de idade removidas", before - len(result))

    before = len(result)
    result = result[result["person_income"].between(config.MIN_INCOME, config.MAX_INCOME)]
    logger.info("Limpeza: %d linhas fora do limite de renda removidas", before - len(result))

    before = len(result)
    result = result[result[config.TARGET].isin([0, 1])]
    logger.info("Limpeza: %d linhas com target inválido removidas", before - len(result))
    return result.reset_index(drop=True)
