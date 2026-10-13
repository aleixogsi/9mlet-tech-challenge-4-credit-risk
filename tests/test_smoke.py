"""Garante que o esqueleto do pacote importa e que a configuração é coerente."""

import importlib

import pytest

from credit_risk import config

MODULES = [
    "credit_risk.data.load",
    "credit_risk.data.clean",
    "credit_risk.data.split",
    "credit_risk.data.privacy",
    "credit_risk.contracts.schemas",
    "credit_risk.contracts.validator",
    "credit_risk.contracts.bad_batch",
    "credit_risk.training.pipeline",
    "credit_risk.training.train",
    "credit_risk.training.evaluate",
    "credit_risk.training.fairness",
    "credit_risk.drift.scenarios",
    "credit_risk.drift.reports",
    "credit_risk.monitoring.prediction_logger",
    "credit_risk.monitoring.health",
    "credit_risk.monitoring.alerts",
    "credit_risk.monitoring.dashboard",
]


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module: str) -> None:
    importlib.import_module(module)


def test_reference_and_production_are_separated() -> None:
    assert config.REFERENCE_DIR != config.PRODUCTION_DIR
    assert config.REFERENCE_FILE.parent == config.REFERENCE_DIR
    assert config.PRODUCTION_BASE_FILE.parent == config.PRODUCTION_DIR


def test_target_is_not_a_feature() -> None:
    assert config.TARGET not in config.FEATURES


def test_drift_thresholds_are_ordered() -> None:
    assert 0 < config.PSI_WARNING < config.PSI_DRIFT


def test_drift_scenarios_file_exists() -> None:
    assert config.DRIFT_SCENARIOS_FILE.exists()
