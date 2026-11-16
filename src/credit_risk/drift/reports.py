"""Detecção de drift com Evidently AI: Referência × Produção.

Os testes estatísticos exigidos pelo enunciado (PSI e Kolmogorov-Smirnov) são calculados
pelo próprio Evidently, configurando o método de drift (`stattest`/`method`) como "psi"
e "ks". Não reimplementamos as estatísticas.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

SCORE_COLUMN = "score"
PREDICTION_COLUMN = "prediction"


def build_drift_report(
    reference: pd.DataFrame, current: pd.DataFrame, output_html: Path
) -> dict[str, Any]:
    """Gera o HTML do Evidently (data drift + prediction drift) e retorna as métricas em dict.

    Usa a API do Evidently 0.7 (versão fixada no uv.lock). O `DataDriftPreset` testa as
    numéricas com KS (threshold `config.KS_PVALUE`) e as categóricas com PSI (threshold
    `config.PSI_DRIFT`), e o veredito do dataset usa `config.ALERT_DRIFT_SHARE`: assim o
    HTML destaca as mesmas features e o mesmo veredito do `drift_summary.json`. O PSI de
    cada numérica entra como `ValueDrift(method="psi")`. Se os dois DataFrames tiverem a
    coluna `score`, mede o prediction drift do score com PSI e KS.

    Retorna `{"evidently": <snapshot.dict()>, "rows": ..., "reference_rows": ...,
    "prediction_drift": {...} | None}`.
    """
    from evidently import DataDefinition, Dataset, Report
    from evidently.metrics import ValueDrift
    from evidently.presets import DataDriftPreset

    from credit_risk import config

    has_score = SCORE_COLUMN in reference.columns and SCORE_COLUMN in current.columns
    numeric = list(config.NUMERIC_FEATURES) + ([SCORE_COLUMN] if has_score else [])
    columns = list(config.FEATURES) + ([SCORE_COLUMN] if has_score else [])
    definition = DataDefinition(
        numerical_columns=numeric, categorical_columns=list(config.CATEGORICAL_FEATURES)
    )
    metrics: list[Any] = [
        DataDriftPreset(
            columns=list(config.FEATURES),
            num_method="ks",
            num_threshold=config.KS_PVALUE,
            cat_method="psi",
            cat_threshold=config.PSI_DRIFT,
            drift_share=config.ALERT_DRIFT_SHARE,
        )
    ]
    metrics += [
        ValueDrift(column=column, method="psi", threshold=config.PSI_DRIFT)
        for column in config.NUMERIC_FEATURES
    ]
    if has_score:
        metrics += [
            ValueDrift(column=SCORE_COLUMN, method="psi", threshold=config.PSI_DRIFT),
            ValueDrift(column=SCORE_COLUMN, method="ks", threshold=config.KS_PVALUE),
        ]
    snapshot = Report(metrics).run(
        Dataset.from_pandas(current[columns], data_definition=definition),
        Dataset.from_pandas(reference[columns], data_definition=definition),
    )
    output_html.parent.mkdir(parents=True, exist_ok=True)
    snapshot.save_html(str(output_html))
    result = snapshot.dict()
    prediction_drift = None
    if has_score:
        values = _value_drift_values(result)
        prediction_drift = {
            "psi": values[(SCORE_COLUMN, "psi")],
            "ks_pvalue": values[(SCORE_COLUMN, "ks")],
            "mean_score_ref": float(reference[SCORE_COLUMN].mean()),
            "mean_score_cur": float(current[SCORE_COLUMN].mean()),
        }
    return {
        "evidently": result,
        "rows": len(current),
        "reference_rows": len(reference),
        "prediction_drift": prediction_drift,
    }


def drift_table(report_metrics: dict[str, Any]) -> pd.DataFrame:
    """Extrai das métricas do Evidently uma tabela por feature.

    Colunas: feature, psi, ks_pvalue, status (stable/warning/drift), drift_detected.
    Alimenta o `drift_summary.json` (formato em context/05-interfaces.md, seção 4).

    `status` segue `config.PSI_WARNING` / `config.PSI_DRIFT`; `drift_detected` é PSI acima
    de `PSI_DRIFT` ou p-valor do KS abaixo de `KS_PVALUE`. Categóricas não têm KS
    (`ks_pvalue` nulo), então o drift delas é decidido só pelo PSI.
    """
    import pandas as pd

    from credit_risk import config

    values = _value_drift_values(report_metrics["evidently"])
    rows = []
    for feature in config.FEATURES:
        if (feature, "psi") not in values:
            raise KeyError(f"PSI ausente nas métricas do Evidently: {feature}")
        psi = float(values[(feature, "psi")])
        ks_pvalue = values.get((feature, "ks"))
        rows.append(
            {
                "feature": feature,
                "psi": psi,
                "ks_pvalue": None if ks_pvalue is None else float(ks_pvalue),
                "status": psi_status(psi),
                "drift_detected": bool(
                    psi > config.PSI_DRIFT
                    or (ks_pvalue is not None and ks_pvalue < config.KS_PVALUE)
                ),
            }
        )
    return pd.DataFrame(rows, columns=["feature", "psi", "ks_pvalue", "status", "drift_detected"])


def psi_status(psi: float) -> str:
    """`stable` (< PSI_WARNING), `warning` (até PSI_DRIFT) ou `drift` (> PSI_DRIFT)."""
    from credit_risk import config

    if psi > config.PSI_DRIFT:
        return "drift"
    if psi >= config.PSI_WARNING:
        return "warning"
    return "stable"


def build_performance_report(
    reference: pd.DataFrame, current: pd.DataFrame, output_html: Path
) -> dict[str, Any]:
    """Relatório de classificação (com rótulo) para evidenciar o concept drift.

    Os DataFrames precisam de `config.TARGET` e `score`. A predição binária usa
    `config.APPROVAL_THRESHOLD`. Gera o HTML do `ClassificationPreset` do Evidently e
    retorna `{"auc", "ks", "auc_reference", "ks_reference", "evidently"}`, em que `auc`
    vem do Evidently e `ks` é a separação máxima entre as distribuições de score de
    bons e maus pagadores (mesma métrica de reports/training/metrics.json).
    """
    from evidently import BinaryClassification, DataDefinition, Dataset, Report
    from evidently.presets import ClassificationPreset

    from credit_risk import config

    definition = DataDefinition(
        classification=[
            BinaryClassification(
                target=config.TARGET,
                prediction_probas=SCORE_COLUMN,
                prediction_labels=PREDICTION_COLUMN,
            )
        ]
    )
    frames = []
    for frame in (current, reference):
        prepared = frame[[config.TARGET, SCORE_COLUMN]].copy()
        prepared[PREDICTION_COLUMN] = (prepared[SCORE_COLUMN] >= config.APPROVAL_THRESHOLD).astype(
            int
        )
        frames.append(Dataset.from_pandas(prepared, data_definition=definition))
    snapshot = Report([ClassificationPreset()]).run(*frames)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    snapshot.save_html(str(output_html))
    result = snapshot.dict()
    auc = next(
        metric["value"]
        for metric in result["metrics"]
        if metric["config"]["type"].endswith(":RocAuc")
    )
    return {
        "auc": float(auc),
        "ks": _score_ks(current),
        "auc_reference": _roc_auc(reference),
        "ks_reference": _score_ks(reference),
        "evidently": result,
    }


def _value_drift_values(evidently_result: dict[str, Any]) -> dict[tuple[str, str], float]:
    """Mapeia (coluna, método) → valor das métricas `ValueDrift` de um snapshot."""
    values = {}
    for metric in evidently_result["metrics"]:
        cfg = metric["config"]
        if cfg["type"].endswith(":ValueDrift"):
            values[(cfg["column"], cfg["method"])] = float(metric["value"])
    return values


def _score_ks(frame: pd.DataFrame) -> float:
    from scipy.stats import ks_2samp

    from credit_risk import config

    positive = frame.loc[frame[config.TARGET] == 1, SCORE_COLUMN]
    negative = frame.loc[frame[config.TARGET] == 0, SCORE_COLUMN]
    if positive.empty or negative.empty:
        return 0.0
    return float(ks_2samp(positive, negative).statistic)


def _roc_auc(frame: pd.DataFrame) -> float | None:
    from sklearn.metrics import roc_auc_score

    from credit_risk import config

    if frame[config.TARGET].nunique() < 2:
        return None
    return float(roc_auc_score(frame[config.TARGET], frame[SCORE_COLUMN]))
