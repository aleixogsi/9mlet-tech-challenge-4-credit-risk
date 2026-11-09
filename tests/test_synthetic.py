"""Testes dos dados sintéticos (T0.5)."""

import pandas as pd

from credit_risk import config
from credit_risk.contracts.schemas import build_training_schema
from tests.fixtures.synthetic import make_synthetic_credit_df, make_synthetic_window


def test_synthetic_df_has_dataset_columns() -> None:
    frame = make_synthetic_credit_df(n=200, seed=1)
    assert list(frame.columns) == [config.ID_COLUMN, *config.FEATURES, config.TARGET]
    assert len(frame) == 200


def test_synthetic_df_passes_training_contract() -> None:
    frame = make_synthetic_credit_df(n=500, seed=2)
    build_training_schema().validate(frame, lazy=True)


def test_synthetic_df_is_reproducible() -> None:
    pd.testing.assert_frame_equal(
        make_synthetic_credit_df(n=100, seed=3), make_synthetic_credit_df(n=100, seed=3)
    )


def test_synthetic_df_has_both_classes() -> None:
    target = make_synthetic_credit_df(n=1_000, seed=4)[config.TARGET]
    assert set(target.unique()) == {0, 1}


def test_optional_score_is_a_probability() -> None:
    score = make_synthetic_credit_df(n=300, seed=5, with_score=True)["score"]
    assert score.between(0, 1).all()


def test_synthetic_window_applies_drift() -> None:
    base = make_synthetic_window(n=300, seed=6)
    drifted = make_synthetic_window(n=300, seed=6, income_factor=1.5, int_rate_shift=3.0)
    ratio = drifted["person_income"].mean() / base["person_income"].mean()
    assert abs(ratio - 1.5) < 0.01
    assert abs((drifted["loan_int_rate"] - base["loan_int_rate"]).mean() - 3.0) < 0.01
