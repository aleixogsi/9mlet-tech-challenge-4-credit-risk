"""Testes de simulação e detecção de drift (Etapa 2)."""

from __future__ import annotations

import copy

import pytest
import yaml

from credit_risk import config
from credit_risk.drift.scenarios import apply_data_drift, load_scenarios, validate_scenarios
from tests.fixtures.synthetic import make_synthetic_credit_df

VALID_SCENARIOS = {
    "seed": 7,
    "windows": [
        {"name": "t1", "changes": []},
        {
            "name": "t2",
            "changes": [
                {
                    "type": "data_drift",
                    "feature": "person_income",
                    "op": "scale",
                    "factor": 1.2,
                    "rationale": "inflação",
                },
                {
                    "type": "concept_drift",
                    "target": config.TARGET,
                    "condition": "loan_percent_income > 0.2",
                    "flip_to": 1,
                    "fraction": 0.5,
                    "rationale": "perda de poder de compra",
                },
            ],
        },
    ],
}


# --- T2.2: cenários e data drift ---------------------------------------------


def test_project_scenarios_file_is_valid() -> None:
    scenarios = load_scenarios(config.DRIFT_SCENARIOS_FILE)
    assert scenarios["windows"]


def test_load_scenarios_reads_yaml(tmp_path) -> None:
    path = tmp_path / "scenarios.yaml"
    path.write_text(yaml.safe_dump(VALID_SCENARIOS), encoding="utf-8")
    assert load_scenarios(path) == VALID_SCENARIOS


def test_load_scenarios_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_scenarios(tmp_path / "missing.yaml")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("rationale", ""),
        ("op", "multiply"),
        ("feature", "loan_grade"),
        ("factor", None),
        ("type", "label_drift"),
    ],
)
def test_invalid_data_drift_change_is_rejected(field: str, value: object) -> None:
    scenarios = copy.deepcopy(VALID_SCENARIOS)
    scenarios["windows"][1]["changes"][0][field] = value
    with pytest.raises(ValueError):
        validate_scenarios(scenarios)


@pytest.mark.parametrize(
    ("field", "value"),
    [("fraction", 0), ("fraction", 1.5), ("flip_to", 2), ("condition", ""), ("target", "x")],
)
def test_invalid_concept_drift_change_is_rejected(field: str, value: object) -> None:
    scenarios = copy.deepcopy(VALID_SCENARIOS)
    scenarios["windows"][1]["changes"][1][field] = value
    with pytest.raises(ValueError):
        validate_scenarios(scenarios)


def test_duplicate_window_names_are_rejected() -> None:
    scenarios = copy.deepcopy(VALID_SCENARIOS)
    scenarios["windows"][1]["name"] = "t1"
    with pytest.raises(ValueError):
        validate_scenarios(scenarios)


def test_scale_scenario_changes_feature() -> None:
    """op=scale altera a média na proporção esperada."""
    frame = make_synthetic_credit_df(n=500, seed=1)
    change = {"feature": "person_income", "op": "scale", "factor": 1.3}
    result = apply_data_drift(frame, change)
    assert result["person_income"].mean() == pytest.approx(frame["person_income"].mean() * 1.3)


def test_shift_scenario_adds_value() -> None:
    frame = make_synthetic_credit_df(n=500, seed=2)
    result = apply_data_drift(frame, {"feature": "loan_int_rate", "op": "shift", "value": 2.5})
    assert (result["loan_int_rate"] - frame["loan_int_rate"]).round(9).eq(2.5).all()


def test_clip_scenario_limits_feature() -> None:
    frame = make_synthetic_credit_df(n=500, seed=3)
    change = {"feature": "person_emp_length", "op": "clip", "min": 2, "max": 5}
    result = apply_data_drift(frame, change)
    assert result["person_emp_length"].between(2, 5).all()


def test_data_drift_does_not_mutate_input() -> None:
    frame = make_synthetic_credit_df(n=100, seed=4)
    original = frame.copy()
    apply_data_drift(frame, {"feature": "person_income", "op": "scale", "factor": 2})
    assert frame.equals(original)


def test_data_drift_keeps_other_columns() -> None:
    frame = make_synthetic_credit_df(n=100, seed=5)
    result = apply_data_drift(frame, {"feature": "person_income", "op": "scale", "factor": 2})
    others = [column for column in frame.columns if column != "person_income"]
    assert result[others].equals(frame[others])
