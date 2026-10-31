"""Etapa 1: treina o baseline na Referência e salva o modelo e as métricas.

Uso: uv run python scripts/train_baseline.py
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

import joblib
from sklearn.model_selection import train_test_split

from credit_risk import config
from credit_risk.contracts.schemas import build_training_schema
from credit_risk.contracts.validator import validate_or_block
from credit_risk.training.evaluate import evaluate, feature_importance
from credit_risk.training.train import train_baseline

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Treinando %s com %s", config.MODEL_VERSION, config.REFERENCE_FILE)
    import pandas as pd

    reference = pd.read_parquet(config.REFERENCE_FILE)
    reference = validate_or_block(reference, build_training_schema(), "reference")
    train, valid = train_test_split(
        reference, test_size=0.2, random_state=config.SEED, stratify=reference[config.TARGET]
    )
    model = train_baseline(train)
    metrics = evaluate(model, valid[config.FEATURES], valid[config.TARGET])
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    config.TRAINING_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config.MODEL_FILE)
    metrics_payload = {
        "model_version": config.MODEL_VERSION,
        "trained_at": datetime.now(UTC).isoformat(),
        "n_train": len(train),
        "n_valid": len(valid),
        **metrics,
        "threshold": config.APPROVAL_THRESHOLD,
    }
    (config.TRAINING_REPORTS_DIR / "metrics.json").write_text(
        json.dumps(metrics_payload, indent=2), encoding="utf-8"
    )
    feature_importance(model).to_csv(
        config.TRAINING_REPORTS_DIR / "feature_importance.csv", index=False
    )
    logger.info("Baseline salvo: AUC %.3f", metrics["auc"])


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
