"""Pipeline sklearn: pré-processamento + classificador."""

from __future__ import annotations

from typing import Any


def build_pipeline(numeric: list[str], categorical: list[str], seed: int) -> Any:
    """Monta o `sklearn.pipeline.Pipeline` (ColumnTransformer + XGBClassifier).

    TODO(T1.8): imputação/one-hot para as categóricas e XGBoost com random_state=seed.
    Opcional: LogisticRegression como modelo de comparação.
    """
    raise NotImplementedError("T1.8")
