"""Exportador Prometheus das métricas de saúde e alertas (T3.7).

Expõe gauges por janela (`window`) e contagens de alertas por severidade/tipo usando
`prometheus_client`, permitindo tanto gravação em arquivo (`reports/monitoring/metrics.prom`)
quanto servidor HTTP (`/metrics`) para coleta pelo Prometheus + Grafana.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING, Any

from prometheus_client import CollectorRegistry, Gauge, generate_latest, start_http_server

if TYPE_CHECKING:
    import pandas as pd


def _is_num(val: Any) -> bool:
    if val is None:
        return False
    try:
        return not math.isnan(float(val))
    except (TypeError, ValueError):
        return False


def build_prometheus_registry(
    health: pd.DataFrame, alerts: list[dict[str, Any]]
) -> CollectorRegistry:
    """Cria e popula um `CollectorRegistry` com as métricas de saúde e alertas."""
    registry = CollectorRegistry()

    g_volume = Gauge(
        "credit_risk_window_volume",
        "Total de predições processadas na janela",
        ["window"],
        registry=registry,
    )
    g_null_pct = Gauge(
        "credit_risk_null_predictions_ratio",
        "Proporção de predições nulas ou com erro na janela",
        ["window"],
        registry=registry,
    )
    g_blocked_pct = Gauge(
        "credit_risk_blocked_batches_ratio",
        "Proporção de lotes bloqueados pelo contrato Pandera na janela",
        ["window"],
        registry=registry,
    )
    g_lat_p50 = Gauge(
        "credit_risk_latency_p50_ms",
        "Latência mediana (p50) de inferência em milissegundos",
        ["window"],
        registry=registry,
    )
    g_lat_p95 = Gauge(
        "credit_risk_latency_p95_ms",
        "Latência p95 de inferência em milissegundos",
        ["window"],
        registry=registry,
    )
    g_mean_score = Gauge(
        "credit_risk_mean_score",
        "Score médio de probabilidade de default na janela",
        ["window"],
        registry=registry,
    )
    g_approval_rate = Gauge(
        "credit_risk_approval_rate",
        "Taxa de aprovação de crédito na janela",
        ["window"],
        registry=registry,
    )
    g_pred_psi = Gauge(
        "credit_risk_prediction_psi",
        "PSI da distribuição do score predito (prediction drift)",
        ["window"],
        registry=registry,
    )
    g_drifted_count = Gauge(
        "credit_risk_drifted_features_count",
        "Quantidade de features com drift detectado na janela",
        ["window"],
        registry=registry,
    )
    g_share_drifted = Gauge(
        "credit_risk_share_drifted",
        "Proporção de features com drift detectado na janela",
        ["window"],
        registry=registry,
    )
    g_auc = Gauge(
        "credit_risk_auc",
        "ROC AUC do modelo na janela de produção",
        ["window"],
        registry=registry,
    )
    g_auc_drop = Gauge(
        "credit_risk_auc_drop",
        "Queda de ROC AUC em relação à referência",
        ["window"],
        registry=registry,
    )
    g_ks = Gauge(
        "credit_risk_ks",
        "Estatística KS de separação do modelo na janela",
        ["window"],
        registry=registry,
    )
    g_alerts = Gauge(
        "credit_risk_alerts_total",
        "Total de alertas disparados por janela, tipo e severidade",
        ["window", "type", "severity"],
        registry=registry,
    )

    for _, row in health.iterrows():
        win = str(row["window"])
        g_volume.labels(window=win).set(float(row.get("volume", 0)))
        g_null_pct.labels(window=win).set(float(row.get("null_predictions_pct", 0.0)))
        g_blocked_pct.labels(window=win).set(float(row.get("blocked_batches_pct", 0.0)))
        g_lat_p50.labels(window=win).set(float(row.get("latency_p50_ms", 0.0)))
        g_lat_p95.labels(window=win).set(float(row.get("latency_p95_ms", 0.0)))
        g_approval_rate.labels(window=win).set(float(row.get("approval_rate", 0.0)))
        g_drifted_count.labels(window=win).set(float(row.get("n_drifted", 0)))
        g_share_drifted.labels(window=win).set(float(row.get("share_drifted", 0.0)))

        if _is_num(row.get("mean_score")):
            g_mean_score.labels(window=win).set(float(row["mean_score"]))
        if _is_num(row.get("prediction_psi")):
            g_pred_psi.labels(window=win).set(float(row["prediction_psi"]))
        if _is_num(row.get("auc")):
            g_auc.labels(window=win).set(float(row["auc"]))
        if _is_num(row.get("auc_drop")):
            g_auc_drop.labels(window=win).set(float(row["auc_drop"]))
        if _is_num(row.get("ks")):
            g_ks.labels(window=win).set(float(row["ks"]))

    counts: dict[tuple[str, str, str], int] = {}
    for alert in alerts:
        key = (
            str(alert.get("window", "unknown")),
            str(alert.get("type", "unknown")),
            str(alert.get("severity", "warning")),
        )
        counts[key] = counts.get(key, 0) + 1

    for (win, a_type, sev), count in counts.items():
        g_alerts.labels(window=win, type=a_type, severity=sev).set(float(count))

    return registry


def render_prometheus_metrics(health: pd.DataFrame, alerts: list[dict[str, Any]]) -> str:
    """Devolve o texto das métricas no formato de exposição do Prometheus."""
    registry = build_prometheus_registry(health, alerts)
    return generate_latest(registry).decode("utf-8")


def write_prometheus_metrics(
    health: pd.DataFrame, alerts: list[dict[str, Any]], output_path: Path
) -> Path:
    """Grava `reports/monitoring/metrics.prom` com as métricas exportadas."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = render_prometheus_metrics(health, alerts)
    output_path.write_text(payload, encoding="utf-8")
    return output_path


def start_metrics_server(
    health: pd.DataFrame, alerts: list[dict[str, Any]], port: int = 8000
) -> CollectorRegistry:
    """Inicia o servidor HTTP Prometheus na porta informada."""
    registry = build_prometheus_registry(health, alerts)
    start_http_server(port, registry=registry)
    return registry
