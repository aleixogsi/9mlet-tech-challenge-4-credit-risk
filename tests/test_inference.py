"""Testes da predição das janelas e dos registros do log (T2.4)."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from credit_risk import config
from credit_risk.inference import (
    PREDICTION_FIELDS,
    build_prediction_records,
    decide,
    get_salt,
    score_in_batches,
)
from credit_risk.training.train import train_baseline
from tests.fixtures.synthetic import make_synthetic_credit_df


@pytest.fixture(scope="module")
def model():
    return train_baseline(make_synthetic_credit_df(n=600, seed=21))


class BrokenModel:
    def predict_proba(self, X):
        raise RuntimeError("boom")


def test_scores_are_probabilities_with_latency(model) -> None:
    frame = make_synthetic_credit_df(n=250, seed=22)
    scores, latencies = score_in_batches(model, frame[config.FEATURES], batch_size=100)
    assert len(scores) == len(latencies) == 250
    assert ((scores >= 0) & (scores <= 1)).all()
    assert (latencies > 0).all()


def test_batched_scores_match_full_prediction(model) -> None:
    frame = make_synthetic_credit_df(n=250, seed=23)
    scores, _ = score_in_batches(model, frame[config.FEATURES], batch_size=7)
    expected = model.predict_proba(frame[config.FEATURES])[:, 1]
    np.testing.assert_allclose(scores, expected, rtol=1e-6)


def test_failed_batch_yields_nan_scores() -> None:
    frame = make_synthetic_credit_df(n=10, seed=24)
    scores, _ = score_in_batches(BrokenModel(), frame[config.FEATURES], batch_size=5)
    assert np.isnan(scores).all()


def test_invalid_batch_size() -> None:
    with pytest.raises(ValueError):
        score_in_batches(BrokenModel(), pd.DataFrame(), batch_size=0)


@pytest.mark.parametrize(
    ("score", "expected"),
    [(0.1, "approved"), (config.APPROVAL_THRESHOLD, "denied"), (0.9, "denied"), (None, "error")],
)
def test_decision_rule(score, expected) -> None:
    assert decide(score, config.APPROVAL_THRESHOLD) == expected


def test_nan_score_is_error() -> None:
    assert decide(math.nan, config.APPROVAL_THRESHOLD) == "error"


def test_records_follow_frozen_format_without_pii() -> None:
    ids = pd.Series(["application_00000001", "application_00000002"])
    records = build_prediction_records(
        ids, np.array([0.2, np.nan]), np.array([1.5, 2.0]), "t3", "salt", "2026-11-01T00:00:00Z"
    )
    assert [tuple(record) for record in records] == [PREDICTION_FIELDS] * 2
    assert records[0]["decision"] == "approved"
    assert records[1]["score"] is None and records[1]["decision"] == "error"
    assert all(record["model_version"] == config.MODEL_VERSION for record in records)
    serialized = str(records)
    assert "application_0000000" not in serialized
    assert len(records[0]["record_id"]) == 64


def test_record_id_depends_on_salt() -> None:
    ids = pd.Series(["application_1"])
    args = (np.array([0.3]), np.array([1.0]), "t1")
    first = build_prediction_records(ids, *args, "salt-a", "ts")[0]["record_id"]
    second = build_prediction_records(ids, *args, "salt-b", "ts")[0]["record_id"]
    assert first != second


def test_empty_salt_is_rejected() -> None:
    with pytest.raises(ValueError):
        build_prediction_records(pd.Series(["x"]), np.array([0.1]), np.array([1.0]), "t1", "", "")


def test_salt_comes_from_environment(monkeypatch) -> None:
    monkeypatch.setenv(config.PSEUDONYMIZATION_SALT_ENV, "segredo")
    assert get_salt() == "segredo"


def test_random_salt_without_environment(monkeypatch) -> None:
    monkeypatch.delenv(config.PSEUDONYMIZATION_SALT_ENV, raising=False)
    assert get_salt() != get_salt()


def _load_predict_script():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).parents[1] / "scripts" / "predict.py"
    spec = importlib.util.spec_from_file_location("predict_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_predict_script_blocks_invalid_window_and_logs_valid(model, tmp_path, monkeypatch):
    import json

    script = _load_predict_script()
    monkeypatch.setattr(config, "PRODUCTION_DIR", tmp_path)
    monkeypatch.setattr(config, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(config, "VALIDATION_LOG", tmp_path / "logs" / "validation.jsonl")
    good = make_synthetic_credit_df(n=50, seed=25)
    bad = good.copy()
    bad.loc[0, "person_age"] = 10
    good.to_parquet(tmp_path / "t1.parquet")
    bad.to_parquet(tmp_path / "t2.parquet")

    assert script.predict_window(model, "t2", "salt") is None
    records = script.predict_window(model, "t1", "salt")
    log = tmp_path / "logs" / "predictions.jsonl"
    assert script.write_log(records, log) == 50
    lines = [json.loads(line) for line in log.read_text().splitlines()]
    assert len(lines) == 50 and set(lines[0]) == set(PREDICTION_FIELDS)
    statuses = [
        json.loads(line)["status"] for line in config.VALIDATION_LOG.read_text().splitlines()
    ]
    assert statuses == ["blocked", "passed"]


def test_predict_script_rejects_unknown_window() -> None:
    with pytest.raises(ValueError):
        _load_predict_script().window_names("t99")
