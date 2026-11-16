"""Métricas de saúde do modelo por janela (documentadas no README, T3.6)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from credit_risk import config

if TYPE_CHECKING:
    pass

VALIDATION_LOG_COLUMNS = [
    "timestamp",
    "batch_name",
    "rows",
    "status",
    "n_failures",
    "failed_rules",
]

HEALTH_COLUMNS = [
    "window",
    "volume",
    "null_predictions_pct",
    "n_batches",
    "n_blocked_batches",
    "blocked_batches_pct",
    "latency_p50_ms",
    "latency_p95_ms",
    "mean_score",
    "reference_mean_score",
    "approval_rate",
    "prediction_psi",
    "n_features",
    "n_drifted",
    "share_drifted",
    "drifted_features",
    "auc",
    "reference_auc",
    "auc_drop",
    "ks",
    "gini",
    "report_html",
]


def read_validation_log(path: Path) -> pd.DataFrame:
    """Lê `logs/validation.jsonl` em um DataFrame (devolve vazio se não existir)."""
    if not path.exists():
        return pd.DataFrame(columns=VALIDATION_LOG_COLUMNS)
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return pd.DataFrame(columns=VALIDATION_LOG_COLUMNS)
    records = [json.loads(line) for line in lines]
    return pd.DataFrame(records, columns=VALIDATION_LOG_COLUMNS)


def read_drift_summary(path: Path) -> dict[str, Any]:
    """Lê `reports/drift/drift_summary.json`."""
    if not path.exists():
        raise FileNotFoundError(f"Resumo de drift não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_reference_auc(
    drift_results: dict[str, Any], windows: list[dict[str, Any]]
) -> float | None:
    """Obtém a AUC de referência via drift_results, metrics.json ou primeira janela (t1)."""
    if "reference_auc" in drift_results and drift_results["reference_auc"] is not None:
        return float(drift_results["reference_auc"])

    metrics_file = config.TRAINING_REPORTS_DIR / "metrics.json"
    if metrics_file.exists():
        try:
            payload = json.loads(metrics_file.read_text(encoding="utf-8"))
            if payload.get("auc") is not None:
                return float(payload["auc"])
        except Exception:
            pass

    for win in windows:
        perf = win.get("performance") or {}
        if perf.get("auc") is not None:
            return float(perf["auc"])
    return None


def compute_health(
    predictions: pd.DataFrame,
    validation_log: pd.DataFrame,
    drift_results: dict[str, Any],
) -> pd.DataFrame:
    """Uma linha por janela com as métricas operacionais, de drift e de performance."""
    drift_windows: list[dict[str, Any]] = list(drift_results.get("windows", []))
    drift_by_window = {str(item["window"]): item for item in drift_windows}

    window_order: list[str] = [str(item["window"]) for item in drift_windows]
    if not predictions.empty and "window" in predictions.columns:
        for win_name in predictions["window"].dropna().astype(str).unique():
            if win_name not in window_order:
                window_order.append(win_name)

    reference_auc = _resolve_reference_auc(drift_results, drift_windows)
    rows: list[dict[str, Any]] = []

    for window in window_order:
        if not predictions.empty and "window" in predictions.columns:
            win_preds = predictions[predictions["window"] == window]
        else:
            win_preds = pd.DataFrame()

        volume = int(len(win_preds))
        if volume > 0:
            is_null_or_err = win_preds["score"].isna() | (win_preds["decision"] == "error")
            null_predictions_pct = float(is_null_or_err.mean())
            latencies = win_preds["latency_ms"].dropna().to_numpy(dtype=float)
            latency_p50_ms = float(np.percentile(latencies, 50)) if len(latencies) > 0 else 0.0
            latency_p95_ms = float(np.percentile(latencies, 95)) if len(latencies) > 0 else 0.0
            valid_scores = win_preds.loc[~is_null_or_err, "score"].astype(float)
            mean_score_pred: float | None = (
                float(valid_scores.mean()) if len(valid_scores) > 0 else None
            )
            valid_decisions = win_preds.loc[~is_null_or_err, "decision"]
            approval_rate = (
                float((valid_decisions == "approved").mean()) if len(valid_decisions) > 0 else 0.0
            )
        else:
            null_predictions_pct = 0.0
            latency_p50_ms = 0.0
            latency_p95_ms = 0.0
            mean_score_pred = None
            approval_rate = 0.0

        if not validation_log.empty and "batch_name" in validation_log.columns:
            win_val = validation_log[validation_log["batch_name"] == window]
            n_batches = int(len(win_val))
            n_blocked_batches = int((win_val["status"] == "blocked").sum())
            blocked_batches_pct = float(n_blocked_batches / n_batches) if n_batches > 0 else 0.0
        else:
            n_batches = 0
            n_blocked_batches = 0
            blocked_batches_pct = 0.0

        drift_info = drift_by_window.get(window, {})
        pred_drift = drift_info.get("prediction_drift") or {}
        perf_info = drift_info.get("performance") or {}
        features_info = drift_info.get("features") or []

        mean_score = (
            mean_score_pred
            if mean_score_pred is not None
            else (
                float(pred_drift["mean_score_cur"])
                if pred_drift.get("mean_score_cur") is not None
                else None
            )
        )
        reference_mean_score = (
            float(pred_drift["mean_score_ref"])
            if pred_drift.get("mean_score_ref") is not None
            else None
        )
        prediction_psi = float(pred_drift["psi"]) if pred_drift.get("psi") is not None else None

        n_features = int(drift_info.get("n_features", len(config.FEATURES)))
        n_drifted = int(drift_info.get("n_drifted", 0))
        share_drifted = float(drift_info.get("share_drifted", 0.0))
        drifted_features = [
            str(f["feature"]) for f in features_info if f.get("drift_detected") is True
        ]

        auc = float(perf_info["auc"]) if perf_info.get("auc") is not None else None
        ks = float(perf_info["ks"]) if perf_info.get("ks") is not None else None
        gini = float(2.0 * auc - 1.0) if auc is not None else None
        auc_drop = (
            float(max(0.0, reference_auc - auc))
            if (auc is not None and reference_auc is not None)
            else None
        )

        rows.append(
            {
                "window": window,
                "volume": volume,
                "null_predictions_pct": null_predictions_pct,
                "n_batches": n_batches,
                "n_blocked_batches": n_blocked_batches,
                "blocked_batches_pct": blocked_batches_pct,
                "latency_p50_ms": latency_p50_ms,
                "latency_p95_ms": latency_p95_ms,
                "mean_score": mean_score,
                "reference_mean_score": reference_mean_score,
                "approval_rate": approval_rate,
                "prediction_psi": prediction_psi,
                "n_features": n_features,
                "n_drifted": n_drifted,
                "share_drifted": share_drifted,
                "drifted_features": drifted_features,
                "auc": auc,
                "reference_auc": reference_auc,
                "auc_drop": auc_drop,
                "ks": ks,
                "gini": gini,
                "report_html": drift_info.get("report_html"),
            }
        )

    health_df = pd.DataFrame(rows, columns=HEALTH_COLUMNS)

    # Preserva informações de lotes bloqueados fora das janelas (ex.: bad_batch na Etapa 1)
    extra_blocked: list[dict[str, Any]] = []
    if not validation_log.empty and "status" in validation_log.columns:
        blocked_rows = validation_log[
            (validation_log["status"] == "blocked")
            & (~validation_log["batch_name"].isin(window_order))
        ]
        for _, row in blocked_rows.iterrows():
            extra_blocked.append(
                {
                    "batch_name": str(row.get("batch_name", "unknown")),
                    "n_failures": int(row.get("n_failures", 0)),
                    "failed_rules": list(row.get("failed_rules", [])),
                }
            )
    health_df.attrs["extra_blocked_batches"] = extra_blocked
    return health_df
