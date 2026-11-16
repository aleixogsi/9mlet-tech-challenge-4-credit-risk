"""Teste de integração da Etapa 2: cenários → janelas → predição → detecção (T2.7).

Roda o fluxo com dados sintéticos e o YAML real do projeto e confere que o
`drift_summary.json` segue a interface congelada (context/05-interfaces.md, seção 4).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

from credit_risk import config
from credit_risk.drift.scenarios import build_windows, load_scenarios
from credit_risk.training.train import train_baseline
from tests.fixtures.synthetic import make_synthetic_credit_df

WINDOW_KEYS = {
    "window",
    "rows",
    "n_features",
    "n_drifted",
    "share_drifted",
    "features",
    "prediction_drift",
    "performance",
    "report_html",
}
FEATURE_KEYS = {"feature", "psi", "ks_pvalue", "status", "drift_detected"}


def _load_script(name: str):
    path = Path(__file__).parents[1] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def drift_run(tmp_path_factory) -> dict:
    """Executa o fluxo da Etapa 2 em dados sintéticos e devolve as entradas do resumo."""
    output_dir = tmp_path_factory.mktemp("drift")
    reference = make_synthetic_credit_df(n=3_000, seed=40)
    production_base = make_synthetic_credit_df(n=3_000, seed=41)
    model = train_baseline(reference)
    scenarios = {**load_scenarios(config.DRIFT_SCENARIOS_FILE), "window_size": 1_500}
    windows = build_windows(production_base, scenarios)
    detect = _load_script("detect_drift")
    scored_reference = detect.with_scores(model, reference)
    entries = {
        name: detect.analyze_window(
            name, scored_reference, detect.with_scores(model, w), output_dir
        )
        for name, w in windows.items()
    }
    return {"entries": entries, "output_dir": output_dir}


def test_summary_entries_follow_interface(drift_run) -> None:
    for entry in drift_run["entries"].values():
        assert set(entry) == WINDOW_KEYS
        assert entry["n_features"] == len(config.FEATURES)
        assert entry["share_drifted"] == pytest.approx(
            entry["n_drifted"] / entry["n_features"], abs=1e-4
        )
        assert set(entry["prediction_drift"]) == {"psi", "mean_score_ref", "mean_score_cur"}
        assert set(entry["performance"]) == {"auc", "ks"}
        for feature in entry["features"]:
            assert set(feature) == FEATURE_KEYS
            assert feature["status"] in {"stable", "warning", "drift"}
    json.dumps(list(drift_run["entries"].values()))


def test_reports_are_written_per_window(drift_run) -> None:
    output_dir = drift_run["output_dir"]
    for name in drift_run["entries"]:
        for filename in (f"drift_{name}.html", f"performance_{name}.html", f"psi_ks_{name}.csv"):
            assert (output_dir / filename).exists()
        table = pd.read_csv(output_dir / f"psi_ks_{name}.csv")
        assert list(table.columns) == ["feature", "psi", "ks_pvalue", "status", "drift_detected"]


def test_control_window_has_no_psi_drift(drift_run) -> None:
    control = drift_run["entries"]["t1"]
    assert all(feature["status"] != "drift" for feature in control["features"])


def test_drift_grows_and_hits_scenario_features(drift_run) -> None:
    entries = drift_run["entries"]
    assert entries["t5"]["n_drifted"] > entries["t1"]["n_drifted"]
    detected = {f["feature"] for f in entries["t5"]["features"] if f["drift_detected"]}
    assert {"loan_int_rate", "loan_percent_income", "person_income"} <= detected


def test_concept_drift_degrades_performance(drift_run) -> None:
    entries = drift_run["entries"]
    assert entries["t5"]["performance"]["auc"] < entries["t1"]["performance"]["auc"]
    assert (
        entries["t5"]["prediction_drift"]["mean_score_cur"]
        > entries["t1"]["prediction_drift"]["mean_score_cur"]
    )
