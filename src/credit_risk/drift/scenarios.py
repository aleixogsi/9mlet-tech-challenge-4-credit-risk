"""Aplica os cenários de configs/drift_scenarios.yaml para gerar as janelas de produção."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

CHANGE_TYPES = {"data_drift", "concept_drift"}
DATA_DRIFT_OPS = {"scale", "shift", "clip"}


def load_scenarios(path: Path) -> dict[str, Any]:
    """Lê e valida o YAML de cenários (cada mudança precisa de `rationale`).

    Lança `ValueError` com a janela e a mudança problemáticas se o arquivo for inválido.
    """
    import yaml

    if not path.exists():
        raise FileNotFoundError(f"Arquivo de cenários não encontrado: {path}")
    scenarios = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate_scenarios(scenarios)
    return scenarios


def validate_scenarios(scenarios: Any) -> None:
    """Valida a estrutura dos cenários: seed, janelas com nome único e mudanças completas."""
    if not isinstance(scenarios, dict):
        raise ValueError("O arquivo de cenários deve ser um mapeamento YAML")
    if not isinstance(scenarios.get("seed"), int):
        raise ValueError("Cenários: 'seed' inteira é obrigatória")
    windows = scenarios.get("windows")
    if not isinstance(windows, list) or not windows:
        raise ValueError("Cenários: 'windows' deve ser uma lista não vazia")
    names = [window.get("name") for window in windows if isinstance(window, dict)]
    if len(names) != len(windows) or not all(isinstance(name, str) and name for name in names):
        raise ValueError("Cenários: toda janela precisa de 'name'")
    if len(set(names)) != len(names):
        raise ValueError(f"Cenários: nomes de janela duplicados: {names}")
    for window in windows:
        changes = window.get("changes", [])
        if not isinstance(changes, list):
            raise ValueError(f"Janela {window['name']}: 'changes' deve ser uma lista")
        for index, change in enumerate(changes):
            _validate_change(change, f"Janela {window['name']}, mudança {index}")


def _validate_change(change: Any, where: str) -> None:
    from credit_risk import config

    if not isinstance(change, dict):
        raise ValueError(f"{where}: a mudança deve ser um mapeamento")
    if change.get("type") not in CHANGE_TYPES:
        raise ValueError(f"{where}: 'type' deve ser um de {sorted(CHANGE_TYPES)}")
    rationale = change.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError(f"{where}: 'rationale' (justificativa econômica) é obrigatória")
    if change["type"] == "data_drift":
        if change.get("feature") not in config.NUMERIC_FEATURES:
            raise ValueError(f"{where}: 'feature' deve ser numérica: {config.NUMERIC_FEATURES}")
        op = change.get("op")
        if op not in DATA_DRIFT_OPS:
            raise ValueError(f"{where}: 'op' deve ser um de {sorted(DATA_DRIFT_OPS)}")
        if op == "scale" and not _is_number(change.get("factor")):
            raise ValueError(f"{where}: op=scale exige 'factor' numérico")
        if op == "shift" and not _is_number(change.get("value")):
            raise ValueError(f"{where}: op=shift exige 'value' numérico")
        if op == "clip":
            low, high = change.get("min"), change.get("max")
            if low is None and high is None:
                raise ValueError(f"{where}: op=clip exige 'min' e/ou 'max'")
            if any(v is not None and not _is_number(v) for v in (low, high)):
                raise ValueError(f"{where}: 'min'/'max' devem ser numéricos")
            if low is not None and high is not None and low > high:
                raise ValueError(f"{where}: 'min' maior que 'max'")
    else:
        if change.get("target") != config.TARGET:
            raise ValueError(f"{where}: 'target' deve ser '{config.TARGET}'")
        condition = change.get("condition")
        if not isinstance(condition, str) or not condition.strip():
            raise ValueError(f"{where}: 'condition' é obrigatória no concept drift")
        if change.get("flip_to") not in (0, 1):
            raise ValueError(f"{where}: 'flip_to' deve ser 0 ou 1")
        fraction = change.get("fraction")
        if not _is_number(fraction) or not 0 < fraction <= 1:
            raise ValueError(f"{where}: 'fraction' deve estar em (0, 1]")


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def apply_data_drift(df: pd.DataFrame, change: dict[str, Any]) -> pd.DataFrame:
    """Altera P(X): operações `scale`, `shift` e `clip` sobre uma feature.

    Devolve uma cópia; o DataFrame de entrada não é modificado.
    """
    feature = change["feature"]
    op = change["op"]
    if feature not in df.columns:
        raise KeyError(f"Feature ausente no DataFrame: {feature}")
    result = df.copy()
    values = result[feature].astype(float)
    if op == "scale":
        result[feature] = values * float(change["factor"])
    elif op == "shift":
        result[feature] = values + float(change["value"])
    elif op == "clip":
        result[feature] = values.clip(lower=change.get("min"), upper=change.get("max"))
    else:
        raise ValueError(f"Operação de data drift desconhecida: {op}")
    return result


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
