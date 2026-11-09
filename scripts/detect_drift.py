"""Etapa 2: compara Referência × cada janela de Produção (PSI/KS + Evidently).

Saídas em reports/drift/: drift_<janela>.html, performance_<janela>.html,
psi_ks_<janela>.csv e drift_summary.json (consumido pelo monitoramento).

Uso: uv run python scripts/detect_drift.py [--window t3]
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from credit_risk import config
from credit_risk.drift.reports import (
    SCORE_COLUMN,
    build_drift_report,
    build_performance_report,
    drift_table,
)
from credit_risk.drift.scenarios import load_scenarios

logger = logging.getLogger(__name__)


def with_scores(model: Any, frame: pd.DataFrame) -> pd.DataFrame:
    """Adiciona a coluna `score` (probabilidade de default) prevista pelo baseline."""
    result = frame.copy()
    result[SCORE_COLUMN] = model.predict_proba(frame[config.FEATURES])[:, 1]
    return result


def relative(path: Path) -> str:
    """Caminho relativo à raiz do projeto (formato do drift_summary.json)."""
    try:
        return path.resolve().relative_to(config.ROOT_DIR).as_posix()
    except ValueError:
        return path.as_posix()


def analyze_window(
    name: str, reference: pd.DataFrame, current: pd.DataFrame, output_dir: Path
) -> dict[str, Any]:
    """Gera os relatórios de uma janela e devolve a entrada dela no drift_summary.json."""
    drift_html = output_dir / f"drift_{name}.html"
    metrics = build_drift_report(reference, current, drift_html)
    table = drift_table(metrics)
    table.to_csv(output_dir / f"psi_ks_{name}.csv", index=False)
    performance = None
    if config.TARGET in current.columns and current[config.TARGET].notna().all():
        perf = build_performance_report(reference, current, output_dir / f"performance_{name}.html")
        performance = {"auc": perf["auc"], "ks": perf["ks"]}
    prediction = metrics["prediction_drift"]
    n_drifted = int(table["drift_detected"].sum())
    return {
        "window": name,
        "rows": len(current),
        "n_features": len(table),
        "n_drifted": n_drifted,
        "share_drifted": round(n_drifted / len(table), 4),
        "features": [
            {
                "feature": row.feature,
                "psi": row.psi,
                "ks_pvalue": None if pd.isna(row.ks_pvalue) else row.ks_pvalue,
                "status": row.status,
                "drift_detected": bool(row.drift_detected),
            }
            for row in table.itertuples()
        ],
        "prediction_drift": None
        if prediction is None
        else {
            "psi": prediction["psi"],
            "mean_score_ref": prediction["mean_score_ref"],
            "mean_score_cur": prediction["mean_score_cur"],
        },
        "performance": performance,
        "report_html": relative(drift_html),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", help="Janela específica (padrão: todas)")
    args = parser.parse_args()
    logger.info("Relatórios em %s", config.DRIFT_REPORTS_DIR)
    names = [w["name"] for w in load_scenarios(config.DRIFT_SCENARIOS_FILE)["windows"]]
    if args.window:
        if args.window not in names:
            raise ValueError(f"Janela desconhecida: {args.window}. Opções: {names}")
        names = [args.window]
    model = joblib.load(config.MODEL_FILE)
    reference = with_scores(model, pd.read_parquet(config.REFERENCE_FILE))
    config.DRIFT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    windows = []
    for name in names:
        path = config.PRODUCTION_DIR / f"{name}.parquet"
        if not path.exists():
            logger.warning("%s: janela não encontrada (%s), rode simulate_drift.py", name, path)
            continue
        entry = analyze_window(
            name, reference, with_scores(model, pd.read_parquet(path)), config.DRIFT_REPORTS_DIR
        )
        drifted = [f["feature"] for f in entry["features"] if f["drift_detected"]]
        logger.info(
            "%s: %d/%d features com drift %s | AUC %s",
            name,
            entry["n_drifted"],
            entry["n_features"],
            drifted,
            "n/d" if entry["performance"] is None else f"{entry['performance']['auc']:.3f}",
        )
        windows.append(entry)
    summary = {
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "reference_rows": len(reference),
        "windows": windows,
    }
    summary_path = config.DRIFT_REPORTS_DIR / "drift_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Resumo salvo em %s", summary_path)
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    raise SystemExit(main())
