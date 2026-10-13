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

    TODO(T1.5): usar `schema.validate(df, lazy=True)` para coletar TODAS as falhas,
    registrar o resultado em config.VALIDATION_LOG (aprovado/bloqueado, regras violadas,
    nº de linhas) e lançar DataContractError quando falhar.
    """
    raise NotImplementedError("T1.5")


def write_validation_report(failures: Any, batch_name: str, output_dir: Path) -> Path:
    """Gera a evidência da falha do contrato em reports/validation/ (HTML ou CSV + resumo).

    TODO(T1.5): tabela com regra violada, coluna, valor e índice. É a prova da Etapa 1.
    """
    raise NotImplementedError("T1.5")
