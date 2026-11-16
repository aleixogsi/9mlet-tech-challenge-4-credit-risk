"""Painel HTML de monitoramento (entregável da Etapa 3).

Mantido simples de propósito: uma página que reúne o que o enunciado pede (métricas de
saúde e alertas de drift) e aponta para os relatórios do Evidently.
"""

from __future__ import annotations

import html
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from credit_risk import config

if TYPE_CHECKING:
    import pandas as pd


def _is_num(val: Any) -> bool:
    if val is None:
        return False
    try:
        return not math.isnan(float(val))
    except (TypeError, ValueError):
        return False


def _fmt_float(val: Any, decimals: int = 3) -> str:
    if not _is_num(val):
        return "—"
    return f"{float(val):.{decimals}f}"


def _fmt_pct(val: Any, decimals: int = 1) -> str:
    if not _is_num(val):
        return "—"
    return f"{float(val) * 100:.{decimals}f}%"


def _cell_class(
    val: Any,
    warn_threshold: float | None = None,
    crit_threshold: float | None = None,
    strict_gt: bool = True,
) -> str:
    if not _is_num(val):
        return ""
    v = float(val)
    if crit_threshold is not None and (v > crit_threshold if strict_gt else v >= crit_threshold):
        return ' class="cell-critical"'
    if warn_threshold is not None and (v > warn_threshold if strict_gt else v >= warn_threshold):
        return ' class="cell-warning"'
    return ' class="cell-ok"'


def _render_kpi_cards(health: pd.DataFrame, alerts: list[dict[str, Any]]) -> str:
    n_windows = len(health)
    total_volume = int(health["volume"].sum()) if "volume" in health.columns and n_windows else 0
    n_crit = sum(1 for a in alerts if a.get("severity") == "critical")
    n_warn = sum(1 for a in alerts if a.get("severity") == "warning")
    max_drift = (
        float(health["share_drifted"].max())
        if "share_drifted" in health.columns and n_windows
        else 0.0
    )
    min_auc = (
        float(health["auc"].dropna().min())
        if "auc" in health.columns and not health["auc"].dropna().empty
        else None
    )
    return f"""
    <section class="kpi-grid">
      <div class="kpi-card">
        <span class="kpi-label">Janelas Monitoradas</span>
        <strong class="kpi-value">{n_windows}</strong>
        <span class="kpi-sub">{total_volume:,} predições auditadas</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Alertas Disparados</span>
        <strong class="kpi-value">{len(alerts)}</strong>
        <span class="kpi-sub">{n_crit} críticos · {n_warn} atenção</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Pico de Data Drift</span>
        <strong class="kpi-value">{_fmt_pct(max_drift, 1)}</strong>
        <span class="kpi-sub">Limiar de alerta: {_fmt_pct(config.ALERT_DRIFT_SHARE, 0)}</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Menor AUC Observada</span>
        <strong class="kpi-value">{_fmt_float(min_auc, 3)}</strong>
        <span class="kpi-sub">Tolerância de queda: -{config.ALERT_AUC_DROP:.2f}</span>
      </div>
    </section>
    """


def _render_health_rows(health: pd.DataFrame) -> str:
    if health.empty:
        return '<tr><td colspan="13">Nenhuma janela monitorada.</td></tr>'

    rows_html: list[str] = []
    for _, row in health.iterrows():
        win = html.escape(str(row["window"]))
        vol = int(row.get("volume", 0))
        null_pct = row.get("null_predictions_pct", 0.0)
        blocked_pct = row.get("blocked_batches_pct", 0.0)
        lat_p50 = row.get("latency_p50_ms", 0.0)
        lat_p95 = row.get("latency_p95_ms", 0.0)
        mean_score = row.get("mean_score")
        approval = row.get("approval_rate", 0.0)
        pred_psi = row.get("prediction_psi")
        n_drifted = int(row.get("n_drifted", 0))
        n_features = int(row.get("n_features", len(config.FEATURES)))
        share_drifted = row.get("share_drifted", 0.0)
        drifted_cols = row.get("drifted_features") or []
        drifted_text = ", ".join(html.escape(str(f)) for f in drifted_cols) if drifted_cols else "—"
        auc = row.get("auc")
        auc_drop = row.get("auc_drop")
        ks = row.get("ks")

        null_cls = _cell_class(
            null_pct,
            warn_threshold=config.ALERT_NULL_PREDICTIONS_PCT,
            crit_threshold=0.05,
        )
        blk_cls = _cell_class(blocked_pct, crit_threshold=0.0)
        lat_cls = _cell_class(
            lat_p95,
            warn_threshold=config.ALERT_LATENCY_P95_MS,
            crit_threshold=2 * config.ALERT_LATENCY_P95_MS,
        )
        psi_cls = _cell_class(
            pred_psi,
            warn_threshold=config.PSI_WARNING,
            crit_threshold=config.PSI_DRIFT,
            strict_gt=False,
        )
        if _is_num(pred_psi) and float(pred_psi) > config.PSI_DRIFT:
            psi_cls = ' class="cell-critical"'
        drift_cls = _cell_class(
            share_drifted,
            crit_threshold=config.ALERT_DRIFT_SHARE,
            strict_gt=False,
        )
        auc_cls = _cell_class(
            auc_drop,
            warn_threshold=config.ALERT_AUC_DROP,
            crit_threshold=2 * config.ALERT_AUC_DROP,
        )

        rows_html.append(
            f"<tr>"
            f"<td><strong>{win}</strong></td>"
            f"<td>{vol:,}</td>"
            f"<td{null_cls}>{_fmt_pct(null_pct, 2)}</td>"
            f"<td{blk_cls}>{_fmt_pct(blocked_pct, 1)}</td>"
            f"<td>{_fmt_float(lat_p50, 2)} ms</td>"
            f"<td{lat_cls}>{_fmt_float(lat_p95, 2)} ms</td>"
            f"<td>{_fmt_float(mean_score, 3)}</td>"
            f"<td>{_fmt_pct(approval, 1)}</td>"
            f"<td{psi_cls}>{_fmt_float(pred_psi, 3)}</td>"
            f"<td{drift_cls}>{n_drifted}/{n_features} ({_fmt_pct(share_drifted, 0)})</td>"
            f'<td class="col-features">{drifted_text}</td>'
            f"<td{auc_cls}>{_fmt_float(auc, 3)} (-{_fmt_float(auc_drop, 3)})</td>"
            f"<td>{_fmt_float(ks, 3)}</td>"
            f"</tr>"
        )
    return "\n".join(rows_html)


def _render_alerts_rows(alerts: list[dict[str, Any]]) -> str:
    if not alerts:
        return '<tr><td colspan="7">Nenhum alerta disparado.</td></tr>'

    rows_html: list[str] = []
    for alert in alerts:
        win = html.escape(str(alert.get("window", "")))
        a_type = html.escape(str(alert.get("type", "")))
        metric = html.escape(str(alert.get("metric", "")))
        val = _fmt_float(alert.get("value"), 4)
        thresh = _fmt_float(alert.get("threshold"), 4)
        sev = html.escape(str(alert.get("severity", "warning")))
        msg = html.escape(str(alert.get("message", "")))
        badge_cls = "badge-critical" if sev == "critical" else "badge-warning"
        rows_html.append(
            f"<tr>"
            f"<td><strong>{win}</strong></td>"
            f'<td><span class="badge {badge_cls}">{sev.upper()}</span></td>'
            f"<td><code>{a_type}</code></td>"
            f"<td><code>{metric}</code></td>"
            f"<td>{val}</td>"
            f"<td>{thresh}</td>"
            f"<td>{msg}</td>"
            f"</tr>"
        )
    return "\n".join(rows_html)


def _render_report_links(health: pd.DataFrame) -> str:
    window_links: list[str] = []
    for _, row in health.iterrows():
        win = html.escape(str(row["window"]))
        window_links.append(
            f"<li>"
            f"<strong>Janela {win}:</strong> "
            f'<a href="../drift/drift_{win}.html">'
            f"Relatório Data &amp; Prediction Drift (HTML)</a> · "
            f'<a href="../drift/performance_{win}.html">'
            f"Relatório Performance / Concept Drift (HTML)</a> · "
            f'<a href="../drift/psi_ks_{win}.csv">Tabela PSI &amp; KS (CSV)</a>'
            f"</li>"
        )
    windows_html = "\n".join(window_links)
    return f"""
    <div class="links-grid">
      <div class="links-box">
        <h3>Relatórios Evidently por Janela (Etapa 2)</h3>
        <ul>
          {windows_html}
          <li>
            <strong>Consolidado:</strong>
            <a href="../drift/drift_summary.json">drift_summary.json</a>
          </li>
        </ul>
      </div>
      <div class="links-box">
        <h3>Contratos de Dados e Baseline (Etapa 1)</h3>
        <ul>
          <li>
            <a href="../validation/bad_batch_failures.csv">
              Evidência de Lote Bloqueado (bad_batch_failures.csv)
            </a>
          </li>
          <li>
            <a href="../training/metrics.json">Métricas do Modelo Baseline (metrics.json)</a>
          </li>
          <li>
            <a href="../training/feature_importance.csv">
              Importância das Features (feature_importance.csv)
            </a>
          </li>
        </ul>
      </div>
    </div>
    """


def build_dashboard(health: pd.DataFrame, alerts: list[dict[str, Any]], output_html: Path) -> Path:
    """Gera `reports/monitoring/index.html` com métricas de saúde, alertas e links."""
    output_html.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    kpi_html = _render_kpi_cards(health, alerts)
    health_rows = _render_health_rows(health)
    alert_rows = _render_alerts_rows(alerts)
    links_html = _render_report_links(health)

    document = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Painel de Observabilidade e Monitoramento — Credit Risk</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --border: #e2e8f0;
      --text: #0f172a;
      --muted: #475569;
      --ok-bg: #f0fdf4;
      --ok-text: #166534;
      --warn-bg: #fefce8;
      --warn-text: #854d0e;
      --crit-bg: #fef2f2;
      --crit-text: #991b1b;
      --accent: #1d4ed8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 2rem;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    header {{
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid var(--border);
    }}
    header h1 {{ margin: 0 0 0.25rem 0; font-size: 1.6rem; }}
    header p {{ margin: 0; color: var(--muted); font-size: 0.92rem; }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .kpi-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.25rem;
      display: flex;
      flex-direction: column;
    }}
    .kpi-label {{
      font-size: 0.82rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .kpi-value {{ font-size: 1.75rem; margin: 0.25rem 0; }}
    .kpi-sub {{ font-size: 0.8rem; color: var(--muted); }}
    section.panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.25rem;
      margin-bottom: 1.75rem;
      overflow-x: auto;
    }}
    section.panel h2 {{ margin-top: 0; font-size: 1.2rem; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
    }}
    th, td {{
      padding: 0.6rem 0.75rem;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: middle;
    }}
    th {{
      background: #f1f5f9;
      font-weight: 600;
      color: #334155;
      white-space: nowrap;
    }}
    td.col-features {{ font-family: monospace; font-size: 0.82rem; max-width: 260px; }}
    td.cell-ok {{ background: var(--ok-bg); color: var(--ok-text); }}
    td.cell-warning {{ background: var(--warn-bg); color: var(--warn-text); font-weight: 600; }}
    td.cell-critical {{ background: var(--crit-bg); color: var(--crit-text); font-weight: 700; }}
    .badge {{
      display: inline-block;
      padding: 0.15rem 0.5rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
    }}
    .badge-warning {{
      background: var(--warn-bg);
      color: var(--warn-text);
      border: 1px solid #fde047;
    }}
    .badge-critical {{
      background: var(--crit-bg);
      color: var(--crit-text);
      border: 1px solid #fca5a5;
    }}
    .links-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.25rem;
    }}
    .links-box h3 {{ margin-top: 0; font-size: 1rem; }}
    .links-box ul {{ margin: 0; padding-left: 1.2rem; }}
    .links-box li {{ margin-bottom: 0.45rem; font-size: 0.9rem; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <h1>
      Painel de Observabilidade e Monitoramento — Credit Risk
      (<code>{html.escape(config.MODEL_VERSION)}</code>)
    </h1>
    <p>
      Saúde operacional do pipeline, detecção de Data/Prediction/Concept Drift
      e alertas de degradação · Gerado em {generated_at}
    </p>
  </header>

  {kpi_html}

  <section class="panel" id="health-metrics">
    <h2>1. Métricas de Saúde por Janela</h2>
    <table>
      <thead>
        <tr>
          <th>Janela</th>
          <th>Volume</th>
          <th>% Nulas/Erro</th>
          <th>% Lotes Bloq.</th>
          <th>Latência p50</th>
          <th>Latência p95</th>
          <th>Score Médio</th>
          <th>Taxa Aprovação</th>
          <th>PSI Score</th>
          <th>Features c/ Drift</th>
          <th>Quais Features</th>
          <th>AUC (Queda)</th>
          <th>KS</th>
        </tr>
      </thead>
      <tbody>
        {health_rows}
      </tbody>
    </table>
  </section>

  <section class="panel" id="degradation-alerts">
    <h2>2. Alertas de Degradação e Qualidade</h2>
    <table>
      <thead>
        <tr>
          <th>Janela / Lote</th>
          <th>Severidade</th>
          <th>Tipo</th>
          <th>Métrica</th>
          <th>Valor</th>
          <th>Threshold</th>
          <th>Mensagem</th>
        </tr>
      </thead>
      <tbody>
        {alert_rows}
      </tbody>
    </table>
  </section>

  <section class="panel" id="evidence-links">
    <h2>3. Relatórios Evidently e Evidências de Auditoria</h2>
    {links_html}
  </section>
</body>
</html>
"""
    output_html.write_text(document, encoding="utf-8")
    return output_html
