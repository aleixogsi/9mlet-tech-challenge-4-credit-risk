"""Análise de vieses do modelo por grupo (evidência para a seção de vieses do README).

Os atributos de grupo (faixa etária e tipo de moradia) servem só para medir disparidade.
A faixa etária é derivada aqui e nunca entra no modelo como feature.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

FAIRNESS_COLUMNS = [
    "group_col",
    "group",
    "n",
    "approval_rate",
    "default_rate",
    "predicted_default_rate",
    "auc",
    "fnr",
    "fpr",
    "approval_ratio",
    "flag_disparity",
]
# Taxas omitidas em grupos pequenos (abaixo de `FAIRNESS_MIN_GROUP_SIZE`).
SUPPRESSED_COLUMNS = [
    "approval_rate",
    "default_rate",
    "predicted_default_rate",
    "fnr",
    "fpr",
    "approval_ratio",
]


def add_age_band(df: pd.DataFrame) -> pd.DataFrame:
    """Devolve uma cópia de `df` com a coluna de faixa etária (`config.AGE_BAND_COLUMN`)."""
    import pandas as pd

    from credit_risk import config

    labels = [label for label, _, _ in config.AGE_BANDS]
    edges = [low for _, low, _ in config.AGE_BANDS] + [config.AGE_BANDS[-1][2] + 1]
    result = df.copy()
    result[config.AGE_BAND_COLUMN] = pd.cut(
        result["person_age"], bins=edges, labels=labels, right=False
    )
    return result


def fairness_by_group(model: Any, df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Métricas por grupo: volume, aprovação, default real, AUC e taxas de erro.

    Colunas (`FAIRNESS_COLUMNS`):

    - `approval_rate`: proporção com score abaixo de `APPROVAL_THRESHOLD`;
    - `default_rate`: default real do grupo;
    - `predicted_default_rate`: score médio (probabilidade prevista de default);
    - `auc`: só para grupos com pelo menos `FAIRNESS_MIN_GROUP_SIZE` linhas e as duas classes;
    - `fnr`: inadimplentes aprovados ÷ inadimplentes (risco para a fintech);
    - `fpr`: bons pagadores negados ÷ bons pagadores (dano ao cliente);
    - `approval_ratio`: aprovação do grupo ÷ maior aprovação entre os grupos;
    - `flag_disparity`: `approval_ratio < FAIRNESS_MIN_RATIO` em grupo com tamanho mínimo.

    Grupos com menos de `FAIRNESS_MIN_GROUP_SIZE` linhas saem só com `n`: as taxas ficam
    vazias (NaN) para o relatório não expor grupos quase individuais (LGPD, minimização).

    Se `group_col` for a faixa etária e ela não existir em `df`, ela é derivada de
    `person_age`. O resultado não tem nenhuma coluna de identificação.
    """
    import numpy as np
    import pandas as pd
    from sklearn.metrics import roc_auc_score

    from credit_risk import config

    if group_col == config.AGE_BAND_COLUMN and group_col not in df.columns:
        df = add_age_band(df)
    if group_col not in df.columns:
        raise KeyError(f"Coluna de grupo ausente: {group_col}")

    scores = pd.Series(model.predict_proba(df[config.FEATURES])[:, 1], index=df.index)
    approved = scores < config.APPROVAL_THRESHOLD
    target = df[config.TARGET].astype(int)

    rows = []
    for group, index in df.groupby(group_col, observed=True).groups.items():
        y = target.loc[index]
        group_scores = scores.loc[index]
        group_approved = approved.loc[index]
        defaults = y == 1
        payers = y == 0
        enough = len(y) >= config.FAIRNESS_MIN_GROUP_SIZE
        rows.append(
            {
                "group_col": group_col,
                "group": str(group),
                "n": int(len(y)),
                "approval_rate": float(group_approved.mean()),
                "default_rate": float(y.mean()),
                "predicted_default_rate": float(group_scores.mean()),
                "auc": (
                    float(roc_auc_score(y, group_scores)) if enough and y.nunique() == 2 else np.nan
                ),
                "fnr": float(group_approved[defaults].mean()) if defaults.any() else np.nan,
                "fpr": float((~group_approved[payers]).mean()) if payers.any() else np.nan,
                "_enough": enough,
            }
        )

    result = pd.DataFrame(rows)
    if result.empty:
        return pd.DataFrame(columns=FAIRNESS_COLUMNS)
    eligible = result.loc[result["_enough"], "approval_rate"]
    best = eligible.max() if not eligible.empty else result["approval_rate"].max()
    result["approval_ratio"] = result["approval_rate"] / best if best > 0 else np.nan
    result["flag_disparity"] = result["_enough"] & (
        result["approval_ratio"] < config.FAIRNESS_MIN_RATIO
    )
    result.loc[~result["_enough"], SUPPRESSED_COLUMNS] = np.nan
    return result[FAIRNESS_COLUMNS].reset_index(drop=True)


def fairness_report(model: Any, df: pd.DataFrame) -> pd.DataFrame:
    """Empilha `fairness_by_group` para todos os grupos de `config.FAIRNESS_GROUPS`."""
    import pandas as pd

    from credit_risk import config

    frames = [fairness_by_group(model, df, group) for group in config.FAIRNESS_GROUPS]
    return pd.concat(frames, ignore_index=True)
