"""Etapas 2 e 3: para cada janela, valida pelo contrato → prediz → grava o log de predições.

Lotes que violam o contrato são BLOQUEADOS (não são preditos) e o bloqueio é logado.

Uso: uv run python scripts/predict.py [--window t3]
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
from credit_risk.contracts.schemas import build_inference_schema
from credit_risk.contracts.validator import DataContractError, validate_or_block
from credit_risk.drift.scenarios import load_scenarios
from credit_risk.inference import build_prediction_records, get_salt, score_in_batches
from credit_risk.monitoring.prediction_logger import log_predictions

logger = logging.getLogger(__name__)


def window_names(selected: str | None) -> list[str]:
    """Janelas do YAML de cenários, ou só a escolhida em --window."""
    names = [window["name"] for window in load_scenarios(config.DRIFT_SCENARIOS_FILE)["windows"]]
    if selected is None:
        return names
    if selected not in names:
        raise ValueError(f"Janela desconhecida: {selected}. Opções: {names}")
    return [selected]


def predict_window(model: Any, name: str, salt: str) -> list[dict[str, Any]] | None:
    """Valida, prediz e devolve os registros do log; devolve None se o lote for bloqueado."""
    frame = pd.read_parquet(config.PRODUCTION_DIR / f"{name}.parquet")
    batch = frame.drop(columns=[config.TARGET], errors="ignore")
    try:
        validated = validate_or_block(batch, build_inference_schema(), name)
    except DataContractError as error:
        logger.error("%s: lote bloqueado pelo contrato, nada foi predito", error)
        return None
    scores, latencies = score_in_batches(
        model, validated[config.FEATURES], config.PREDICTION_BATCH_SIZE
    )
    timestamp = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return build_prediction_records(
        validated[config.ID_COLUMN], scores, latencies, name, salt, timestamp
    )


def write_log(records: list[dict[str, Any]], path: Path) -> int:
    """Grava pelo logger centralizado (T3.1); enquanto ele não existe, anexa o JSONL direto."""
    try:
        return log_predictions(records, path)
    except NotImplementedError:
        # TODO(T3.1): remover este fallback quando log_predictions estiver implementado.
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return len(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", help="Janela específica (padrão: todas)")
    args = parser.parse_args()
    logger.info("Modelo: %s | janela: %s", config.MODEL_FILE, args.window or "todas")
    model = joblib.load(config.MODEL_FILE)
    salt = get_salt()
    for name in window_names(args.window):
        records = predict_window(model, name, salt)
        if records is None:
            continue
        written = write_log(records, config.PREDICTIONS_LOG)
        denied = sum(record["decision"] == "denied" for record in records)
        logger.info(
            "%s: %d predições gravadas | %.1f%% negadas", name, written, 100 * denied / written
        )
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    raise SystemExit(main())
