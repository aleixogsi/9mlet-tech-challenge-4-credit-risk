"""Log centralizado de predições (JSONL), SEM PII.

Formato de cada linha: interface congelada, ver context/05-interfaces.md (seção 2).
    {
      "timestamp": "2026-01-01T00:00:00Z",
      "window": "t3",
      "record_id": "<hash pseudonimizado>",
      "score": 0.42,                # probabilidade de default (null se falhou)
      "decision": "approved",       # approved | denied | error
      "latency_ms": 3.1,
      "model_version": "baseline_v1"
    }
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from credit_risk.inference import PREDICTION_FIELDS

if TYPE_CHECKING:
    import pandas as pd

VALID_DECISIONS = frozenset({"approved", "denied", "error"})
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def _validate_record(record: dict[str, Any]) -> dict[str, Any]:
    """Garante que o registro segue o contrato congelado e não contém PII."""
    keys = set(record.keys())
    expected = set(PREDICTION_FIELDS)
    if keys != expected:
        extra = sorted(keys - expected)
        missing = sorted(expected - keys)
        raise ValueError(f"Registro de predição inválido (extras={extra}, ausentes={missing})")

    record_id = record["record_id"]
    if not isinstance(record_id, str) or not SHA256_HEX_RE.match(record_id):
        raise ValueError(
            "record_id deve ser um hash SHA-256 hexadecimal de 64 caracteres (sem PII em claro)"
        )

    decision = record["decision"]
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Decisão inválida: {decision!r}. Esperado: {sorted(VALID_DECISIONS)}")

    raw_score = record["score"]
    if raw_score is None or (isinstance(raw_score, float) and math.isnan(raw_score)):
        score: float | None = None
    else:
        score = float(raw_score)
        if not (0.0 <= score <= 1.0):
            raise ValueError(f"score fora do intervalo [0, 1]: {score}")

    latency_ms = float(record["latency_ms"])
    if math.isnan(latency_ms) or latency_ms < 0.0:
        raise ValueError(f"latency_ms inválido: {latency_ms}")

    timestamp = str(record["timestamp"])
    window = str(record["window"])
    model_version = str(record["model_version"])
    if not timestamp or not window or not model_version:
        raise ValueError("timestamp, window e model_version são obrigatórios")

    return {
        "timestamp": timestamp,
        "window": window,
        "record_id": record_id,
        "score": score,
        "decision": decision,
        "latency_ms": latency_ms,
        "model_version": model_version,
    }


def log_predictions(records: Iterable[dict[str, Any]], path: Path) -> int:
    """Anexa os registros validados ao JSONL e retorna quantos foram gravados."""
    validated = [_validate_record(record) for record in records]
    if not validated:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for item in validated:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    return len(validated)


def read_predictions(path: Path) -> pd.DataFrame:
    """Lê o JSONL de predições e devolve um DataFrame validado."""
    import pandas as pd

    if not path.exists():
        raise FileNotFoundError(f"Log de predições não encontrado: {path}")

    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return pd.DataFrame(columns=list(PREDICTION_FIELDS))

    records = [_validate_record(json.loads(line)) for line in lines]
    return pd.DataFrame(records, columns=list(PREDICTION_FIELDS))
