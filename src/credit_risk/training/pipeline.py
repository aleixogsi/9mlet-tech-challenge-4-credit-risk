"""Pipeline sklearn: pré-processamento + classificador."""

from __future__ import annotations

from typing import Any


def build_pipeline(numeric: list[str], categorical: list[str], seed: int) -> Any:
    """Monta o `sklearn.pipeline.Pipeline` (ColumnTransformer + XGBClassifier).

    XGBoost é usado conforme a decisão D4 da arquitetura.
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    from xgboost import XGBClassifier

    numeric_transformer = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        [
            ("numeric", numeric_transformer, numeric),
            ("categorical", categorical_transformer, categorical),
        ]
    )
    classifier = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        random_state=seed,
        n_jobs=1,
    )
    return Pipeline([("preprocessor", preprocessor), ("classifier", classifier)])
