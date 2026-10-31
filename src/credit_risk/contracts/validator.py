"""Validação bloqueante: dados que violam o contrato NÃO seguem para o modelo."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


class DataContractError(Exception):
    """Lançada quando um lote viola o contrato. A ingestão é bloqueada."""

    def __init__(self, batch_name: str, failures: Any) -> None:
        self.batch_name = batch_name
        self.failures = failures
        super().__init__(f"Lote '{batch_name}' bloqueado: violou o contrato de dados")


def validate_or_block(df: pd.DataFrame, schema: Any, batch_name: str) -> pd.DataFrame:
    """Valida o lote e devolve o DataFrame validado, ou lança DataContractError.

    A validação é a única porta de entrada para os scripts de treino e predição.
    """
    from datetime import UTC, datetime

    from pandera.errors import SchemaErrors

    from credit_risk import config

    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        validated = schema.validate(df, lazy=True)
    except SchemaErrors as error:
        failures = error.failure_cases
        rules = sorted(
            {str(value) for value in failures["check"].dropna().tolist()}
        )
        _append_log(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "batch_name": batch_name,
                "rows": len(df),
                "status": "blocked",
                "n_failures": len(failures),
                "failed_rules": rules,
            }
        )
        raise DataContractError(batch_name, failures) from error
    _append_log(
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "batch_name": batch_name,
            "rows": len(df),
            "status": "passed",
            "n_failures": 0,
            "failed_rules": [],
        }
    )
    return validated


def write_validation_report(failures: Any, batch_name: str, output_dir: Path) -> Path:
    """Gera a evidência da falha do contrato em reports/validation/ (HTML ou CSV + resumo).

    O CSV evita depender de uma biblioteca de renderização HTML.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{batch_name}_failures.csv"
    failures.to_csv(output, index=False)
    return output


def _append_log(entry: dict[str, Any]) -> None:
    import json

    from credit_risk import config

    with config.VALIDATION_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
