"""Gera apresentacao/demo/data.js com os números reais da execução versionada.

Fontes: reports/training/metrics.json, reports/drift/drift_summary.json e logs/*.jsonl.
Se data/ existir localmente, inclui também os histogramas reais de loan_int_rate
(Referência × janelas t1..t5) para a cena 3. Nada aqui tem PII: o log já traz o
record_id pseudonimizado, e a página só mostra o começo e o fim do hash.

Uso (na raiz do repositório):
    uv run python apresentacao/demo/build_data.py
"""

from __future__ import annotations

import json
import random
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "data.js"
WINDOWS = ["t1", "t2", "t3", "t4", "t5"]
RATE_EDGES = list(np.arange(5.0, 29.0, 1.0))  # faixas de 1 p.p. entre 5% e 28%


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def short_id(record_id: str) -> str:
    return f"{record_id[:8]}…{record_id[-4:]}"


def window_health(predictions: list[dict], window: str) -> dict:
    rows = [p for p in predictions if p["window"] == window]
    latencies = np.array([p["latency_ms"] for p in rows], dtype=float)
    approved = sum(p["decision"] == "approved" for p in rows)
    errors = sum(p["decision"] == "error" or p["score"] is None for p in rows)
    return {
        "volume": len(rows),
        "approved": approved,
        "denied": len(rows) - approved - errors,
        "errors": errors,
        "approval_rate": approved / len(rows) if rows else None,
        "latency_p50": float(np.percentile(latencies, 50)) if rows else None,
        "latency_p95": float(np.percentile(latencies, 95)) if rows else None,
    }


def prediction_sample(predictions: list[dict], window: str, size: int = 60) -> list[dict]:
    rows = [p for p in predictions if p["window"] == window and p["score"] is not None]
    rng = random.Random(42)
    picked = rng.sample(rows, min(size, len(rows)))
    return [
        {
            "id": short_id(p["record_id"]),
            "score": round(p["score"], 4),
            "decision": p["decision"],
            "latency": round(min(p["latency_ms"], 9.9), 2),
        }
        for p in picked
    ]


def rate_histograms() -> dict | None:
    """Densidade de loan_int_rate por faixa de 1 p.p.; None se data/ não existir."""
    import pandas as pd

    files = {"reference": ROOT / "data" / "reference" / "reference.parquet"}
    files.update({w: ROOT / "data" / "production" / f"{w}.parquet" for w in WINDOWS})
    if not all(path.exists() for path in files.values()):
        return None
    result: dict = {"edges": RATE_EDGES}
    for name, path in files.items():
        values = pd.read_parquet(path, columns=["loan_int_rate"])["loan_int_rate"].dropna()
        counts, _ = np.histogram(values.clip(RATE_EDGES[0], RATE_EDGES[-1] - 1e-6), RATE_EDGES)
        result[name] = {
            "density": [round(c / counts.sum(), 5) for c in counts],
            "mean": round(float(values.mean()), 2),
        }
    return result


def concept_share(window: str = "t5") -> float | None:
    """% dos rótulos da janela trocados pelo concept drift (comparando com a base de produção)."""
    import pandas as pd

    base_path = ROOT / "data" / "production" / "production_base.parquet"
    win_path = ROOT / "data" / "production" / f"{window}.parquet"
    if not (base_path.exists() and win_path.exists()):
        return None
    base = pd.read_parquet(base_path, columns=["application_id", "loan_status"])
    win = pd.read_parquet(win_path, columns=["application_id", "loan_status"])
    merged = win.merge(base, on="application_id", suffixes=("", "_base"))
    return round(float((merged["loan_status"] != merged["loan_status_base"]).mean() * 100), 1)


def build() -> dict:
    """Monta os dados da página a partir dos artefatos versionados (e de data/, se existir)."""
    metrics = json.loads((ROOT / "reports/training/metrics.json").read_text(encoding="utf-8"))
    summary = json.loads((ROOT / "reports/drift/drift_summary.json").read_text(encoding="utf-8"))
    predictions = read_jsonl(ROOT / "logs/predictions.jsonl")
    validation = read_jsonl(ROOT / "logs/validation.jsonl")
    alerts = read_jsonl(ROOT / "logs/alerts.jsonl")

    windows = []
    for item in summary["windows"]:
        name = item["window"]
        windows.append(
            {
                "window": name,
                **window_health(predictions, name),
                "n_features": item["n_features"],
                "n_drifted": item["n_drifted"],
                "share_drifted": item["share_drifted"],
                "prediction_psi": item["prediction_drift"]["psi"],
                "mean_score": item["prediction_drift"]["mean_score_cur"],
                "auc": (item.get("performance") or {}).get("auc"),
                "ks": (item.get("performance") or {}).get("ks"),
                "features": [
                    {
                        "feature": f["feature"],
                        "psi": f["psi"],
                        "ks_pvalue": f.get("ks_pvalue"),
                        "status": f["status"],
                        "drift": f["drift_detected"],
                    }
                    for f in item["features"]
                ],
            }
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "model": {"version": metrics["model_version"], "auc": metrics["auc"]},
        "reference_mean_score": summary["windows"][0]["prediction_drift"]["mean_score_ref"],
        "windows": windows,
        "validation": [
            {k: v[k] for k in ("batch_name", "rows", "status", "n_failures", "failed_rules")}
            for v in validation
        ],
        "alerts": [
            {k: a[k] for k in ("window", "type", "metric", "value", "threshold", "severity")}
            for a in alerts
        ],
        "sample": {w: prediction_sample(predictions, w) for w in ("t1", "t5")},
        "rate_hist": rate_histograms(),
        "concept_t5": concept_share("t5"),
    }


def main() -> None:
    data = build()
    OUT.write_text(
        "// Gerado por build_data.py a partir dos artefatos versionados. Não edite à mão.\n"
        f"window.DEMO_DATA = {json.dumps(data, ensure_ascii=False)};\n",
        encoding="utf-8",
    )
    volume = sum(w["volume"] for w in data["windows"])
    print(f"{OUT} · {volume} predições · {len(data['alerts'])} alertas")


if __name__ == "__main__":
    main()
