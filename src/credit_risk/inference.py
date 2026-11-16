"""Predição das janelas de produção e montagem dos registros do log (Etapa 2, T2.4).

Os registros seguem o formato congelado de `logs/predictions.jsonl`
(context/05-interfaces.md, seção 2) e nunca contêm PII: o `application_id` é
pseudonimizado com salt antes de sair desta função.
"""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

logger = logging.getLogger(__name__)

PREDICTION_FIELDS = (
    "timestamp",
    "window",
    "record_id",
    "score",
    "decision",
    "latency_ms",
    "model_version",
)


def score_in_batches(
    model: Any, features: pd.DataFrame, batch_size: int
) -> tuple[np.ndarray, np.ndarray]:
    """Calcula a probabilidade de default em micro-lotes e mede a latência.

    Retorna `(scores, latency_ms)`, ambos com uma posição por registro. A latência de um
    registro é o tempo da chamada `predict_proba` do micro-lote em que ele foi predito.
    Se um micro-lote falhar, os seus registros ficam com score `NaN` (decisão `error`).
    """
    import time

    import numpy as np

    if batch_size < 1:
        raise ValueError("batch_size deve ser positivo")
    scores = np.full(len(features), np.nan)
    latencies = np.zeros(len(features))
    for start in range(0, len(features), batch_size):
        chunk = features.iloc[start : start + batch_size]
        began = time.perf_counter()
        try:
            chunk_scores = model.predict_proba(chunk)[:, 1]
        except Exception:  # a falha vira decisão "error" no log
            logger.exception("Falha ao predizer o micro-lote iniciado em %d", start)
            chunk_scores = np.full(len(chunk), np.nan)
        elapsed_ms = (time.perf_counter() - began) * 1000
        scores[start : start + len(chunk)] = chunk_scores
        latencies[start : start + len(chunk)] = elapsed_ms
    return scores, latencies


def decide(score: float | None, threshold: float) -> str:
    """`approved` se score < threshold, `denied` caso contrário e `error` sem score."""
    if score is None or (isinstance(score, float) and math.isnan(score)):
        return "error"
    return "approved" if score < threshold else "denied"


def build_prediction_records(
    ids: pd.Series,
    scores: np.ndarray,
    latencies_ms: np.ndarray,
    window: str,
    salt: str,
    timestamp: str,
) -> list[dict[str, Any]]:
    """Monta os registros do log de predições, um por proposta, sem PII."""
    from credit_risk import config
    from credit_risk.data.privacy import pseudonymize_id

    if not salt:
        raise ValueError("O salt da pseudonimização não pode ser vazio")
    if not len(ids) == len(scores) == len(latencies_ms):
        raise ValueError("ids, scores e latências devem ter o mesmo tamanho")
    records = []
    for raw_id, raw_score, latency in zip(ids, scores, latencies_ms, strict=True):
        score = None if math.isnan(float(raw_score)) else float(raw_score)
        records.append(
            {
                "timestamp": timestamp,
                "window": window,
                "record_id": pseudonymize_id(str(raw_id), salt),
                "score": score,
                "decision": decide(score, config.APPROVAL_THRESHOLD),
                "latency_ms": round(float(latency), 4),
                "model_version": config.MODEL_VERSION,
            }
        )
    return records


def get_salt() -> str:
    """Lê o salt da variável de ambiente; sem ela, usa um salt aleatório desta execução.

    O salt aleatório mantém o log sem PII, mas os `record_id` deixam de ser estáveis
    entre execuções. Para rastreabilidade, defina a variável no `.env`.
    """
    import os
    import secrets

    from credit_risk import config

    salt = os.environ.get(config.PSEUDONYMIZATION_SALT_ENV, "")
    if salt:
        return salt
    logger.warning(
        "%s não definido: usando salt aleatório (record_id não é estável entre execuções)",
        config.PSEUDONYMIZATION_SALT_ENV,
    )
    return secrets.token_hex(16)
