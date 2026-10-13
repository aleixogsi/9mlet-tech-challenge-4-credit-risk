"""Central configuration: paths, seeds, schema columns and monitoring thresholds.

Nada de caminhos absolutos ou números mágicos espalhados pelo código: tudo que for
parâmetro do projeto vive aqui (ver context/02-convencoes.md).
"""

from __future__ import annotations

from pathlib import Path

# --- Paths -------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
REFERENCE_DIR = DATA_DIR / "reference"
PRODUCTION_DIR = DATA_DIR / "production"
BAD_BATCHES_DIR = DATA_DIR / "bad_batches"

MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"
VALIDATION_REPORTS_DIR = REPORTS_DIR / "validation"
TRAINING_REPORTS_DIR = REPORTS_DIR / "training"
DRIFT_REPORTS_DIR = REPORTS_DIR / "drift"
MONITORING_REPORTS_DIR = REPORTS_DIR / "monitoring"
LOGS_DIR = ROOT_DIR / "logs"
CONFIGS_DIR = ROOT_DIR / "configs"

RAW_DATASET_FILE = RAW_DIR / "credit_risk_dataset.csv"
REFERENCE_FILE = REFERENCE_DIR / "reference.parquet"
PRODUCTION_BASE_FILE = PRODUCTION_DIR / "production_base.parquet"
BAD_BATCH_FILE = BAD_BATCHES_DIR / "bad_batch.parquet"
MODEL_FILE = MODELS_DIR / "baseline_v1.joblib"
DRIFT_SCENARIOS_FILE = CONFIGS_DIR / "drift_scenarios.yaml"

PREDICTIONS_LOG = LOGS_DIR / "predictions.jsonl"
VALIDATION_LOG = LOGS_DIR / "validation.jsonl"
ALERTS_LOG = LOGS_DIR / "alerts.jsonl"

# --- Reproducibility ---------------------------------------------------------
SEED = 42
REFERENCE_FRACTION = 0.6  # fração do dataset limpo que vira Referência (treino)
MODEL_VERSION = "baseline_v1"

# --- Dataset schema (Credit Risk Dataset, Kaggle) ----------------------------
# TODO(T0.2): confirmar os nomes das colunas após baixar o dataset.
ID_COLUMN = "application_id"  # criado em prepare_data.py; nunca logado em claro
TARGET = "loan_status"
NUMERIC_FEATURES = [
    "person_age",
    "person_income",
    "person_emp_length",
    "loan_amnt",
    "loan_int_rate",
    "loan_percent_income",
    "cb_person_cred_hist_length",
]
CATEGORICAL_FEATURES = [
    "person_home_ownership",
    "loan_intent",
    "loan_grade",
    "cb_person_default_on_file",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# --- Data contract limits (Etapa 1) ------------------------------------------
MIN_AGE = 18
MAX_AGE = 100
MIN_INCOME = 1.0
MAX_INCOME = 10_000_000.0

# --- Drift thresholds (Etapa 2): aplicados aos testes PSI/KS do Evidently -----
PSI_WARNING = 0.10  # 0.10–0.25: atenção
PSI_DRIFT = 0.25  # > 0.25: drift
KS_PVALUE = 0.05  # p-valor < 0.05: distribuições diferentes

# --- Health / alert thresholds (Etapa 3) -------------------------------------
APPROVAL_THRESHOLD = 0.5  # score de default acima disso → crédito negado
ALERT_DRIFT_SHARE = 0.30  # alerta se ≥ 30% das features derivarem
ALERT_NULL_PREDICTIONS_PCT = 0.01  # alerta se > 1% de predições nulas
ALERT_LATENCY_P95_MS = 200.0
ALERT_AUC_DROP = 0.05  # alerta se a AUC cair mais que 0.05 vs. referência
