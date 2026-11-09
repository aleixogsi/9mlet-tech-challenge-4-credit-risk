"""Testes de simulação e detecção de drift (Etapa 2)."""

from __future__ import annotations

import copy

import pandas as pd
import pytest
import yaml

from credit_risk import config
from credit_risk.drift.reports import (
    build_drift_report,
    build_performance_report,
    drift_table,
    psi_status,
)
from credit_risk.drift.scenarios import (
    apply_concept_drift,
    apply_data_drift,
    build_windows,
    load_scenarios,
    validate_scenarios,
)
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


# --- T2.3: concept drift e janelas --------------------------------------------


def test_concept_drift_changes_only_target() -> None:
    """Concept drift altera loan_status e mantém as features."""
    import numpy as np

    frame = make_synthetic_credit_df(n=1_000, seed=6)
    change = VALID_SCENARIOS["windows"][1]["changes"][1]
    result = apply_concept_drift(frame, change, np.random.default_rng(0))
    assert result[config.FEATURES].equals(frame[config.FEATURES])
    assert result[config.TARGET].sum() > frame[config.TARGET].sum()


def test_concept_drift_respects_condition_and_fraction() -> None:
    import numpy as np

    frame = make_synthetic_credit_df(n=2_000, seed=7)
    change = VALID_SCENARIOS["windows"][1]["changes"][1]
    result = apply_concept_drift(frame, change, np.random.default_rng(0))
    inside = frame.eval(change["condition"])
    eligible = inside & (frame[config.TARGET] == 0)
    flipped = result[config.TARGET] != frame[config.TARGET]
    assert not flipped[~inside].any()
    assert (result.loc[flipped, config.TARGET] == 1).all()
    assert flipped.sum() == round(0.5 * eligible.sum())


def test_windows_are_reproducible() -> None:
    """Mesma seed → mesmas janelas."""
    base = make_synthetic_credit_df(n=800, seed=8)
    scenarios = {**VALID_SCENARIOS, "window_size": 300}
    first, second = build_windows(base, scenarios), build_windows(base, scenarios)
    assert first.keys() == second.keys()
    for name in first:
        pd.testing.assert_frame_equal(first[name], second[name])


def test_windows_change_with_seed() -> None:
    base = make_synthetic_credit_df(n=800, seed=9)
    first = build_windows(base, {**VALID_SCENARIOS, "window_size": 300})
    other = build_windows(base, {**VALID_SCENARIOS, "window_size": 300, "seed": 8})
    assert not first["t1"].equals(other["t1"])


def test_windows_have_dataset_columns_and_size() -> None:
    base = make_synthetic_credit_df(n=800, seed=10)
    windows = build_windows(base, {**VALID_SCENARIOS, "window_size": 300})
    assert list(windows) == ["t1", "t2"]
    for frame in windows.values():
        assert list(frame.columns) == list(base.columns)
        assert len(frame) == 300
        assert frame[config.ID_COLUMN].is_unique


def test_control_window_keeps_distribution() -> None:
    base = make_synthetic_credit_df(n=800, seed=11)
    window = build_windows(base, {**VALID_SCENARIOS, "window_size": 300})["t1"]
    assert set(window[config.ID_COLUMN]) <= set(base[config.ID_COLUMN])
    merged = window.merge(base, on=config.ID_COLUMN, suffixes=("", "_base"))
    assert (merged["person_income"] == merged["person_income_base"]).all()


def test_window_size_is_capped_by_base() -> None:
    base = make_synthetic_credit_df(n=100, seed=12)
    windows = build_windows(base, {**VALID_SCENARIOS, "window_size": 10_000})
    assert all(len(frame) == 100 for frame in windows.values())


def test_project_windows_pass_inference_contract() -> None:
    from credit_risk.contracts.schemas import build_inference_schema

    base = make_synthetic_credit_df(n=3_000, seed=13)
    scenarios = {**load_scenarios(config.DRIFT_SCENARIOS_FILE), "window_size": 1_000}
    for frame in build_windows(base, scenarios).values():
        build_inference_schema().validate(frame.drop(columns=[config.TARGET]), lazy=True)


@pytest.mark.parametrize("size", [0, -5, 1.5, "100"])
def test_invalid_window_size_is_rejected(size: object) -> None:
    with pytest.raises(ValueError):
        validate_scenarios({**VALID_SCENARIOS, "window_size": size})


# --- T2.1: cenários alinhados à feature importance ----------------------------


def test_project_scenarios_cover_data_and_concept_drift() -> None:
    scenarios = load_scenarios(config.DRIFT_SCENARIOS_FILE)
    types = {c["type"] for w in scenarios["windows"] for c in w.get("changes", [])}
    assert types == {"data_drift", "concept_drift"}
    assert scenarios["windows"][0]["changes"] == []


def test_project_scenarios_drift_top_numeric_features() -> None:
    """As ≥ 2 features numéricas mais importantes do baseline sofrem data drift."""
    importance = pd.read_csv(config.TRAINING_REPORTS_DIR / "feature_importance.csv")
    numeric = importance[importance["feature"].isin(config.NUMERIC_FEATURES)]
    top_two = set(numeric["feature"].head(2))
    scenarios = load_scenarios(config.DRIFT_SCENARIOS_FILE)
    drifted = {
        c["feature"]
        for w in scenarios["windows"]
        for c in w["changes"]
        if c["type"] == "data_drift"
    }
    assert top_two <= drifted
    assert len(drifted) >= 2


def test_project_scenarios_intensity_grows() -> None:
    scenarios = load_scenarios(config.DRIFT_SCENARIOS_FILE)
    counts = [len(w["changes"]) for w in scenarios["windows"]]
    assert counts == sorted(counts)


# --- T2.6: detecção com Evidently (PSI e KS) ----------------------------------


@pytest.fixture(scope="module")
def reference_frame() -> pd.DataFrame:
    return make_synthetic_credit_df(n=2_000, seed=30, with_score=True)


@pytest.mark.parametrize(
    ("psi", "status"),
    [(0.0, "stable"), (config.PSI_WARNING, "warning"), (0.2, "warning"), (0.3, "drift")],
)
def test_psi_status_thresholds(psi: float, status: str) -> None:
    assert psi_status(psi) == status


def test_identical_data_has_no_drift(reference_frame, tmp_path) -> None:
    """Referência × ela mesma → nenhuma feature com status 'drift'."""
    metrics = build_drift_report(reference_frame, reference_frame, tmp_path / "same.html")
    table = drift_table(metrics)
    assert list(table["feature"]) == config.FEATURES
    assert (table["status"] == "stable").all()
    assert not table["drift_detected"].any()
    assert metrics["prediction_drift"]["psi"] == pytest.approx(0.0, abs=1e-9)


def test_shifted_feature_is_flagged(reference_frame, tmp_path) -> None:
    """Feature fortemente deslocada → status 'drift' na drift_table (PSI e KS)."""
    current = reference_frame.copy()
    current["loan_int_rate"] = current["loan_int_rate"] + 5
    table = drift_table(build_drift_report(reference_frame, current, tmp_path / "d.html"))
    row = table.set_index("feature").loc["loan_int_rate"]
    assert row["status"] == "drift"
    assert row["psi"] > config.PSI_DRIFT
    assert row["ks_pvalue"] < config.KS_PVALUE
    assert bool(row["drift_detected"])
    assert table.set_index("feature").loc["person_age", "status"] == "stable"


def test_categorical_features_have_no_ks(reference_frame, tmp_path) -> None:
    table = drift_table(build_drift_report(reference_frame, reference_frame, tmp_path / "c.html"))
    categorical = table[table["feature"].isin(config.CATEGORICAL_FEATURES)]
    numeric = table[table["feature"].isin(config.NUMERIC_FEATURES)]
    assert categorical["ks_pvalue"].isna().all()
    assert numeric["ks_pvalue"].notna().all()


def test_drift_report_writes_html(reference_frame, tmp_path) -> None:
    output = tmp_path / "nested" / "drift.html"
    build_drift_report(reference_frame, reference_frame, output)
    assert output.exists()
    assert "<html" in output.read_text(encoding="utf-8")[:2_000].lower()


def test_drift_report_without_score_has_no_prediction_drift(reference_frame, tmp_path) -> None:
    frame = reference_frame.drop(columns=["score"])
    assert build_drift_report(frame, frame, tmp_path / "n.html")["prediction_drift"] is None


def test_prediction_drift_follows_score_shift(reference_frame, tmp_path) -> None:
    current = reference_frame.copy()
    current["score"] = (current["score"] + 0.3).clip(upper=1.0)
    prediction = build_drift_report(reference_frame, current, tmp_path / "p.html")[
        "prediction_drift"
    ]
    assert prediction["psi"] > config.PSI_DRIFT
    assert prediction["mean_score_cur"] > prediction["mean_score_ref"]


def test_performance_report_drops_with_concept_drift(reference_frame, tmp_path) -> None:
    import numpy as np

    stable = build_performance_report(reference_frame, reference_frame, tmp_path / "s.html")
    current = reference_frame.copy()
    rng = np.random.default_rng(0)
    flip = rng.random(len(current)) < 0.3
    current.loc[flip, config.TARGET] = 1 - current.loc[flip, config.TARGET]
    drifted = build_performance_report(reference_frame, current, tmp_path / "c.html")
    assert (tmp_path / "c.html").exists()
    assert stable["auc"] == pytest.approx(stable["auc_reference"], abs=1e-6)
    assert drifted["auc"] < stable["auc"] - 0.1
    assert drifted["ks"] < stable["ks"]
