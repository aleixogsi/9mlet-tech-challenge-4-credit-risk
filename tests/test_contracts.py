"""Testes do contrato de dados da Etapa 1."""

import pandas as pd
import pytest

from credit_risk import config
from credit_risk.contracts.bad_batch import make_bad_batch
from credit_risk.contracts.schemas import build_training_schema
from credit_risk.contracts.validator import DataContractError, validate_or_block


def valid_frame(rows: int = 8) -> pd.DataFrame:
    return pd.DataFrame(
        {
            config.ID_COLUMN: [f"id-{i}" for i in range(rows)],
            "person_age": [30.0] * rows,
            "person_income": [50_000.0] * rows,
            "person_emp_length": [5.0] * rows,
            "loan_amnt": [10_000.0] * rows,
            "loan_int_rate": [10.0] * rows,
            "loan_percent_income": [0.2] * rows,
            "cb_person_cred_hist_length": [5.0] * rows,
            "person_home_ownership": ["RENT"] * rows,
            "loan_intent": ["PERSONAL"] * rows,
            "loan_grade": ["B"] * rows,
            "cb_person_default_on_file": ["N"] * rows,
            config.TARGET: [0, 1] * (rows // 2),
        }
    )


def assert_blocked(frame: pd.DataFrame) -> None:
    with pytest.raises(DataContractError):
        validate_or_block(frame, build_training_schema(), "test")


def test_reference_passes_contract() -> None:
    assert len(validate_or_block(valid_frame(), build_training_schema(), "reference")) == 8


def test_underage_is_blocked() -> None:
    frame = valid_frame()
    frame.loc[0, "person_age"] = 17
    assert_blocked(frame)


def test_null_income_is_blocked() -> None:
    frame = valid_frame()
    frame.loc[0, "person_income"] = None
    assert_blocked(frame)


def test_duplicate_rows_are_blocked() -> None:
    frame = valid_frame()
    frame.loc[1] = frame.loc[0].copy()
    assert_blocked(frame)


def test_invalid_income_is_blocked() -> None:
    frame = valid_frame()
    frame.loc[0, "person_income"] = config.MAX_INCOME + 1
    assert_blocked(frame)


def test_invalid_category_is_blocked() -> None:
    frame = valid_frame()
    frame.loc[0, "loan_grade"] = "Z"
    assert_blocked(frame)


def test_invalid_target_is_blocked() -> None:
    frame = valid_frame()
    frame.loc[0, config.TARGET] = 2
    assert_blocked(frame)


def test_bad_batch_violates_every_rule() -> None:
    batch = make_bad_batch(valid_frame(), config.SEED)
    assert_blocked(batch)
