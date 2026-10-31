"""Métricas de performance do modelo (baseline e janelas de produção com rótulo)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def evaluate(model: Any, X: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    """Retorna AUC, KS, Gini, F1, precisão e recall.

    As métricas são calculadas no conjunto de validação separado do treino.
    """
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    auc = roc_auc_score(y, probabilities)
    ks = _ks_statistic(y, probabilities)
    return {
        "auc": float(auc),
        "ks": float(ks),
        "gini": float(2 * auc - 1),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "accuracy": float(accuracy_score(y, predictions)),
    }


def feature_importance(model: Any) -> pd.DataFrame:
    """Importância das features, usada para escolher quais variáveis sofrerão drift (T2.1).

    Retorna a importância agregada por feature original após one-hot encoding.
    """
    import pandas as pd

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]
    names = preprocessor.get_feature_names_out()
    values = classifier.feature_importances_
    result = pd.DataFrame({"feature": names, "importance": values})
    original_features = [
        *preprocessor.transformers_[0][2],
        *preprocessor.transformers_[1][2],
    ]
    result["feature"] = result["feature"].map(
        lambda value: next(
            feature
            for feature in original_features
            if value.split("__", maxsplit=1)[-1].startswith(feature)
        )
    )
    return (
        result.groupby("feature", as_index=False)["importance"]
        .sum()
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def _ks_statistic(y: pd.Series, scores: Any) -> float:
    import numpy as np

    positive = np.asarray(scores)[np.asarray(y) == 1]
    negative = np.asarray(scores)[np.asarray(y) == 0]
    if not len(positive) or not len(negative):
        return 0.0
    positive_sorted = np.sort(positive)
    negative_sorted = np.sort(negative)
    values = np.sort(np.unique(np.concatenate([positive_sorted, negative_sorted])))
    return float(
        np.max(
            np.abs(
                np.searchsorted(positive_sorted, values, side="right") / len(positive_sorted)
                - np.searchsorted(negative_sorted, values, side="right") / len(negative_sorted)
            )
        )
    )
