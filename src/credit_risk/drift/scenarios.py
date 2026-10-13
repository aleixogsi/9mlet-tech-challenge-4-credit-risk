"""Aplica os cenários de configs/drift_scenarios.yaml para gerar as janelas de produção."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd


def load_scenarios(path: Path) -> dict[str, Any]:
    """Lê e valida o YAML de cenários (cada mudança precisa de `rationale`).

    TODO(T2.2)
    """
    raise NotImplementedError("T2.2")


def apply_data_drift(df: pd.DataFrame, change: dict[str, Any]) -> pd.DataFrame:
    """Altera P(X): operações `scale`, `shift` e `clip` sobre uma feature.

    TODO(T2.2)
    """
    raise NotImplementedError("T2.2")


def apply_concept_drift(
    df: pd.DataFrame, change: dict[str, Any], rng: np.random.Generator
) -> pd.DataFrame:
    """Altera P(y|X): muda o target de uma fração das linhas que atendem a `condition`.

    TODO(T2.3)
    """
    raise NotImplementedError("T2.3")


def build_windows(
    production_base: pd.DataFrame, scenarios: dict[str, Any]
) -> dict[str, pd.DataFrame]:
    """Gera {nome_da_janela: DataFrame} aplicando as mudanças de cada janela, com seed fixa.

    TODO(T2.3): cada janela amostra da base de produção e aplica as mudanças.
    """
    raise NotImplementedError("T2.3")
