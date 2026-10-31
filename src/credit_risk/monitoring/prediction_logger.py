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

from collections.abc import Iterable
from pathlib import Path
from typing import Any


def log_predictions(records: Iterable[dict[str, Any]], path: Path) -> int:
    """Anexa os registros ao JSONL e retorna quantos foram gravados.

    TODO(T3.1): validar se nenhum campo fora do formato acima (ex.: PII) é gravado.
    """
    raise NotImplementedError("T3.1")


def read_predictions(path: Path) -> Any:
    """Lê o JSONL de predições em um DataFrame.

    TODO(T3.1)
    """
    raise NotImplementedError("T3.1")
