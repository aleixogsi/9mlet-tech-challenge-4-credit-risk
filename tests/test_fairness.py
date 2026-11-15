"""Testes do relatório de vieses (T4.3) com dados sintéticos e modelos fake."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from credit_risk import config
from credit_risk.training.fairness import (
    FAIRNESS_COLUMNS,
    SUPPRESSED_COLUMNS,
    add_age_band,
    fairness_by_group,
    fairness_report,
)
from credit_risk.training.train import split_reference
from tests.fixtures.synthetic import make_synthetic_credit_df


class RuleModel:
    """Modelo fake: a probabilidade de default vem de uma regra sobre as features."""

    def __init__(self, rule) -> None:
        self.rule = rule

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        probability = np.asarray(self.rule(X), dtype=float)
        return np.column_stack([1 - probability, probability])


def interest_model() -> RuleModel:
    """Score crescente com a taxa de juros: tem sinal, mas não olha para o grupo."""
    return RuleModel(lambda X: np.clip((X["loan_int_rate"] - 5) / 20, 0, 1))


@pytest.fixture
def frame() -> pd.DataFrame:
    return make_synthetic_credit_df(n=2_000, seed=7)


def test_report_has_expected_columns_and_ranges(frame: pd.DataFrame) -> None:
    report = fairness_report(interest_model(), frame)

    assert list(report.columns) == FAIRNESS_COLUMNS
    assert set(report["group_col"]) == set(config.FAIRNESS_GROUPS)
    for group_col in config.FAIRNESS_GROUPS:
        assert report.loc[report["group_col"] == group_col, "n"].sum() == len(frame)
    for column in ["approval_rate", "default_rate", "predicted_default_rate", "fnr", "fpr"]:
        values = report[column].dropna()
        assert values.between(0, 1).all(), column
    assert report["flag_disparity"].dtype == bool


def test_group_with_lower_approval_is_flagged(frame: pd.DataFrame) -> None:
    model = RuleModel(lambda X: np.where(X["person_home_ownership"] == "RENT", 0.9, 0.1))

    result = fairness_by_group(model, frame, "person_home_ownership").set_index("group")

    assert result.loc["RENT", "approval_rate"] == 0.0
    assert result.loc["RENT", "flag_disparity"]
    assert not result.loc["MORTGAGE", "flag_disparity"]
    assert result.loc["MORTGAGE", "approval_ratio"] == pytest.approx(1.0)


def test_single_class_group_does_not_break(frame: pd.DataFrame) -> None:
    data = frame.copy()
    data.loc[data["person_home_ownership"] == "OWN", config.TARGET] = 0

    result = fairness_by_group(interest_model(), data, "person_home_ownership")
    own = result.set_index("group").loc["OWN"]

    assert np.isnan(own["auc"])
    assert np.isnan(own["fnr"])
    assert own["default_rate"] == 0.0


def test_small_group_gets_no_auc_and_no_flag(frame: pd.DataFrame) -> None:
    data = frame.copy()
    data.loc[data.index[:5], "person_home_ownership"] = "OTHER"
    data.loc[data.index[5:], "person_home_ownership"] = data.loc[
        data.index[5:], "person_home_ownership"
    ].replace("OTHER", "RENT")
    model = RuleModel(lambda X: np.where(X["person_home_ownership"] == "OTHER", 0.9, 0.1))

    other = fairness_by_group(model, data, "person_home_ownership").set_index("group").loc["OTHER"]

    assert other["n"] == 5
    assert np.isnan(other["auc"])
    assert not other["flag_disparity"]


def test_small_group_rates_are_suppressed(frame: pd.DataFrame) -> None:
    data = frame.copy()
    data.loc[data.index[:5], "person_home_ownership"] = "OTHER"
    data.loc[data.index[5:], "person_home_ownership"] = data.loc[
        data.index[5:], "person_home_ownership"
    ].replace("OTHER", "RENT")

    result = fairness_by_group(interest_model(), data, "person_home_ownership").set_index("group")

    assert result.loc["OTHER", SUPPRESSED_COLUMNS].isna().all()
    assert result.loc["RENT", SUPPRESSED_COLUMNS].notna().all()


def test_result_has_no_identifier(frame: pd.DataFrame) -> None:
    report = fairness_report(interest_model(), frame)

    assert config.ID_COLUMN not in report.columns
    assert not report.astype(str).isin(frame[config.ID_COLUMN].tolist()).any().any()


def test_age_bands_follow_config_limits() -> None:
    ages = pd.DataFrame({"person_age": [18.0, 25.0, 26.0, 45.0, 46.0, 60.0, 61.0, 100.0]})

    result = add_age_band(ages)

    assert result[config.AGE_BAND_COLUMN].astype(str).tolist() == [
        "18-25",
        "18-25",
        "26-35",
        "36-45",
        "46-60",
        "46-60",
        "61+",
        "61+",
    ]
    assert config.AGE_BAND_COLUMN not in ages.columns
    assert config.AGE_BAND_COLUMN not in config.FEATURES


def test_age_band_is_derived_when_missing(frame: pd.DataFrame) -> None:
    result = fairness_by_group(interest_model(), frame, config.AGE_BAND_COLUMN)

    labels = [label for label, _, _ in config.AGE_BANDS]
    assert set(result["group"]) <= set(labels)
    assert result["n"].sum() == len(frame)


def test_split_reference_is_reproducible_and_stratified(frame: pd.DataFrame) -> None:
    train_a, valid_a = split_reference(frame)
    train_b, valid_b = split_reference(frame)

    assert len(valid_a) == round(len(frame) * config.VALIDATION_FRACTION)
    assert valid_a[config.ID_COLUMN].tolist() == valid_b[config.ID_COLUMN].tolist()
    assert set(train_a[config.ID_COLUMN]).isdisjoint(valid_a[config.ID_COLUMN])
    assert valid_a[config.TARGET].mean() == pytest.approx(frame[config.TARGET].mean(), abs=0.01)
    assert len(train_b) == len(train_a)
