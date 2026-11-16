"""Regras de alerta sobre as métricas de saúde e de drift."""

from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from credit_risk import config

if TYPE_CHECKING:
    import pandas as pd

ALERT_TYPES = frozenset(
    {
        "data_drift",
        "prediction_drift",
        "performance_drop",
        "null_predictions",
        "latency",
        "contract_blocked",
    }
)
ALERT_SEVERITIES = frozenset({"warning", "critical"})
ALERT_FIELDS = (
    "timestamp",
    "window",
    "type",
    "metric",
    "value",
    "threshold",
    "severity",
    "message",
)


def _is_valid_number(value: Any) -> bool:
    if value is None:
        return False
    try:
        return not math.isnan(float(value))
    except (TypeError, ValueError):
        return False


def _make_alert(
    timestamp: str,
    window: str,
    alert_type: str,
    metric: str,
    value: float,
    threshold: float,
    severity: str,
    message: str,
) -> dict[str, Any]:
    if alert_type not in ALERT_TYPES:
        raise ValueError(f"Tipo de alerta inválido: {alert_type}")
    if severity not in ALERT_SEVERITIES:
        raise ValueError(f"Severidade inválida: {severity}")
    return {
        "timestamp": timestamp,
        "window": str(window),
        "type": alert_type,
        "metric": metric,
        "value": round(float(value), 4),
        "threshold": round(float(threshold), 4),
        "severity": severity,
        "message": message,
    }


def evaluate_alerts(health: pd.DataFrame) -> list[dict[str, Any]]:
    """Compara as métricas de saúde com os thresholds ALERT_* de config.py.

    Retorna uma lista de dicionários no formato congelado de `logs/alerts.jsonl`.
    """
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    alerts: list[dict[str, Any]] = []

    for blocked in health.attrs.get("extra_blocked_batches", []):
        batch_name = str(blocked.get("batch_name", "unknown"))
        n_failures = int(blocked.get("n_failures", 0))
        rules = blocked.get("failed_rules") or []
        rules_suffix = f" [{', '.join(str(r) for r in rules)}]" if rules else ""
        alerts.append(
            _make_alert(
                timestamp=timestamp,
                window=batch_name,
                alert_type="contract_blocked",
                metric="blocked_batches_pct",
                value=1.0,
                threshold=0.0,
                severity="critical",
                message=(
                    f"Lote '{batch_name}' bloqueado pelo contrato de dados "
                    f"({n_failures} violações){rules_suffix}"
                ),
            )
        )

    for _, row in health.iterrows():
        win = str(row["window"])

        blocked_pct = row.get("blocked_batches_pct", 0.0)
        if _is_valid_number(blocked_pct) and float(blocked_pct) > 0.0:
            alerts.append(
                _make_alert(
                    timestamp=timestamp,
                    window=win,
                    alert_type="contract_blocked",
                    metric="blocked_batches_pct",
                    value=float(blocked_pct),
                    threshold=0.0,
                    severity="critical",
                    message=(
                        f"{float(blocked_pct):.0%} dos lotes bloqueados pelo contrato "
                        f"na janela {win}"
                    ),
                )
            )

        share_drifted = row.get("share_drifted", 0.0)
        if _is_valid_number(share_drifted) and float(share_drifted) >= config.ALERT_DRIFT_SHARE:
            drifted_cols = row.get("drifted_features") or []
            cols_text = f" ({', '.join(str(c) for c in drifted_cols)})" if drifted_cols else ""
            alerts.append(
                _make_alert(
                    timestamp=timestamp,
                    window=win,
                    alert_type="data_drift",
                    metric="share_drifted",
                    value=float(share_drifted),
                    threshold=config.ALERT_DRIFT_SHARE,
                    severity="critical",
                    message=(
                        f"{float(share_drifted):.0%} das features com drift na janela "
                        f"{win}{cols_text}"
                    ),
                )
            )

        pred_psi = row.get("prediction_psi")
        if _is_valid_number(pred_psi):
            psi_val = float(pred_psi)
            if psi_val > config.PSI_DRIFT:
                alerts.append(
                    _make_alert(
                        timestamp=timestamp,
                        window=win,
                        alert_type="prediction_drift",
                        metric="prediction_psi",
                        value=psi_val,
                        threshold=config.PSI_DRIFT,
                        severity="critical",
                        message=(
                            f"PSI do score ({psi_val:.3f}) acima do limite crítico "
                            f"({config.PSI_DRIFT:.2f}) na janela {win}"
                        ),
                    )
                )
            elif psi_val >= config.PSI_WARNING:
                alerts.append(
                    _make_alert(
                        timestamp=timestamp,
                        window=win,
                        alert_type="prediction_drift",
                        metric="prediction_psi",
                        value=psi_val,
                        threshold=config.PSI_WARNING,
                        severity="warning",
                        message=(
                            f"PSI do score ({psi_val:.3f}) em faixa de atenção "
                            f"(>= {config.PSI_WARNING:.2f}) na janela {win}"
                        ),
                    )
                )

        auc_drop = row.get("auc_drop")
        if _is_valid_number(auc_drop) and float(auc_drop) > config.ALERT_AUC_DROP:
            drop_val = float(auc_drop)
            auc_val = row.get("auc")
            auc_str = f" (AUC={float(auc_val):.3f})" if _is_valid_number(auc_val) else ""
            severity = "critical" if drop_val >= 2 * config.ALERT_AUC_DROP else "warning"
            alerts.append(
                _make_alert(
                    timestamp=timestamp,
                    window=win,
                    alert_type="performance_drop",
                    metric="auc_drop",
                    value=drop_val,
                    threshold=config.ALERT_AUC_DROP,
                    severity=severity,
                    message=(
                        f"Queda de AUC de {drop_val:.3f}{auc_str} acima do limite "
                        f"({config.ALERT_AUC_DROP:.2f}) na janela {win}"
                    ),
                )
            )

        null_pct = row.get("null_predictions_pct", 0.0)
        if _is_valid_number(null_pct) and float(null_pct) > config.ALERT_NULL_PREDICTIONS_PCT:
            null_val = float(null_pct)
            severity = "critical" if null_val >= 0.05 else "warning"
            alerts.append(
                _make_alert(
                    timestamp=timestamp,
                    window=win,
                    alert_type="null_predictions",
                    metric="null_predictions_pct",
                    value=null_val,
                    threshold=config.ALERT_NULL_PREDICTIONS_PCT,
                    severity=severity,
                    message=(
                        f"{null_val:.1%} de predições nulas/erro na janela {win} "
                        f"(limite: {config.ALERT_NULL_PREDICTIONS_PCT:.1%})"
                    ),
                )
            )

        latency_p95 = row.get("latency_p95_ms", 0.0)
        if _is_valid_number(latency_p95) and float(latency_p95) > config.ALERT_LATENCY_P95_MS:
            lat_val = float(latency_p95)
            severity = "critical" if lat_val >= 2 * config.ALERT_LATENCY_P95_MS else "warning"
            alerts.append(
                _make_alert(
                    timestamp=timestamp,
                    window=win,
                    alert_type="latency",
                    metric="latency_p95_ms",
                    value=lat_val,
                    threshold=config.ALERT_LATENCY_P95_MS,
                    severity=severity,
                    message=(
                        f"Latência p95 de {lat_val:.1f} ms acima do limite "
                        f"({config.ALERT_LATENCY_P95_MS:.1f} ms) na janela {win}"
                    ),
                )
            )

    return alerts


def write_alerts(alerts: list[dict[str, Any]], path: Path) -> None:
    """Anexa os alertas validados em `logs/alerts.jsonl`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for alert in alerts:
            missing = sorted(set(ALERT_FIELDS) - set(alert.keys()))
            if missing:
                raise ValueError(f"Alerta com campos obrigatórios ausentes: {missing}")
            ordered = {field: alert[field] for field in ALERT_FIELDS}
            handle.write(json.dumps(ordered, ensure_ascii=False) + "\n")
