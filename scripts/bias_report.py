"""Etapa 4: gera o relatório de vieses do modelo em reports/training/.

- `fairness.csv`: métricas por faixa etária e por tipo de moradia no holdout de validação
  da Referência (o mesmo do treino do baseline);
- `fairness_windows.csv`: as mesmas métricas por faixa etária em cada janela de produção
  (t1…tN), para ver se a crise simulada pesa mais sobre algum grupo. Só é gerado se as
  janelas já existirem (rode `simulate_drift.py` antes).

Uso: uv run python scripts/bias_report.py
"""

from __future__ import annotations

import logging

import joblib
import pandas as pd

from credit_risk import config
from credit_risk.drift.scenarios import load_scenarios
from credit_risk.training.fairness import fairness_by_group, fairness_report
from credit_risk.training.train import split_reference

logger = logging.getLogger(__name__)

FAIRNESS_FILE = config.TRAINING_REPORTS_DIR / "fairness.csv"
FAIRNESS_WINDOWS_FILE = config.TRAINING_REPORTS_DIR / "fairness_windows.csv"


def windows_report(model: object) -> pd.DataFrame | None:
    """Métricas por faixa etária em cada janela de produção que existir em disco."""
    names = [window["name"] for window in load_scenarios(config.DRIFT_SCENARIOS_FILE)["windows"]]
    frames = []
    for name in names:
        path = config.PRODUCTION_DIR / f"{name}.parquet"
        if not path.exists():
            continue
        result = fairness_by_group(model, pd.read_parquet(path), config.AGE_BAND_COLUMN)
        result.insert(0, "window", name)
        frames.append(result)
    return pd.concat(frames, ignore_index=True) if frames else None


def main() -> None:
    model = joblib.load(config.MODEL_FILE)
    reference = pd.read_parquet(config.REFERENCE_FILE)
    _, valid = split_reference(reference)
    config.TRAINING_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report = fairness_report(model, valid)
    report.to_csv(FAIRNESS_FILE, index=False, float_format="%.4f")
    flagged = report.loc[report["flag_disparity"], ["group_col", "group", "approval_ratio"]]
    logger.info("Relatório de vieses (%d linhas de validação) → %s", len(valid), FAIRNESS_FILE)
    for row in flagged.itertuples(index=False):
        logger.warning(
            "Disparidade de aprovação: %s=%s (razão %.2f < %.2f)",
            row.group_col,
            row.group,
            row.approval_ratio,
            config.FAIRNESS_MIN_RATIO,
        )

    windows = windows_report(model)
    if windows is None:
        logger.info("Janelas de produção ausentes: fairness_windows.csv não foi gerado")
        return
    windows.to_csv(FAIRNESS_WINDOWS_FILE, index=False, float_format="%.4f")
    logger.info("Vieses por janela → %s", FAIRNESS_WINDOWS_FILE)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
