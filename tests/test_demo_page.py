"""Testes da página de demonstração do vídeo (apresentacao/demo/, D19).

A página mostra os números de `data.js`, gerado por `build_data.py` a partir dos artefatos
versionados. Os testes garantem que esses números batem com `logs/` e `reports/` e que nenhum
ID completo sai na página.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType

import pytest

from credit_risk import config

DEMO_DIR = config.ROOT_DIR / "apresentacao" / "demo"
DATA_JS = DEMO_DIR / "data.js"
# A latência muda a cada execução do pipeline; o resto é reprodutível com a seed.
VOLATILE_KEYS = {"latency_p50", "latency_p95"}


def load_module(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"demo_{name}", DEMO_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_data_js(path: Path = DATA_JS) -> dict:
    text = path.read_text(encoding="utf-8")
    return json.loads(text[text.index("{") : text.rindex("}") + 1])


def stable(windows: list[dict]) -> list[dict]:
    return [{k: v for k, v in w.items() if k not in VOLATILE_KEYS} for w in windows]


@pytest.fixture(scope="module")
def page_data() -> dict:
    if not DATA_JS.exists():
        pytest.skip("apresentacao/demo/data.js não existe")
    return read_data_js()


def test_page_numbers_match_versioned_artifacts(page_data: dict) -> None:
    if not (config.LOGS_DIR / "predictions.jsonl").exists():
        pytest.skip("logs/ da execução final não estão presentes")
    fresh = load_module("build_data").build()
    assert page_data["model"] == fresh["model"]
    assert page_data["validation"] == fresh["validation"]
    assert page_data["alerts"] == fresh["alerts"], "rode apresentacao/demo/build_data.py"
    assert stable(page_data["windows"]) == stable(fresh["windows"])


def test_page_has_no_full_record_id(page_data: dict) -> None:
    assert not re.search(r"[0-9a-f]{64}", DATA_JS.read_text(encoding="utf-8"))
    short = re.compile(r"^[0-9a-f]{8}…[0-9a-f]{4}$")
    ids = [row["id"] for rows in page_data["sample"].values() for row in rows]
    assert ids
    assert all(short.match(i) for i in ids)


def test_risk_level_bands() -> None:
    serve = load_module("serve")
    assert serve.risk_level(0.05) == "Baixo"
    assert serve.risk_level(serve.LOW_RISK) == "Moderado"
    assert serve.risk_level(config.APPROVAL_THRESHOLD) == "Alto"


def test_last_record_takes_the_latest_batch(tmp_path: Path) -> None:
    serve = load_module("serve")
    log = tmp_path / "validation.jsonl"
    rows = [
        {"batch_name": "bad_batch", "n_failures": 3},
        {"batch_name": "t1", "n_failures": 0},
        {"batch_name": "bad_batch", "n_failures": 8},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    assert serve._last_record(log, "bad_batch")["n_failures"] == 8
    assert serve._last_record(tmp_path / "missing.jsonl", "bad_batch") is None
