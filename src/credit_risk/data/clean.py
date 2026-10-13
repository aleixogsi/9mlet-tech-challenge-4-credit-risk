"""Limpeza do dataset bruto para gerar a base limpa (origem da Referência)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove/corrige registros inválidos para que a Referência passe no contrato.

    TODO(T1.1): tratar nulos (ex.: person_emp_length, loan_int_rate), idades fora de
    [MIN_AGE, MAX_AGE], rendas fora dos limites e duplicatas. Logar quantas linhas
    cada regra removeu: isso entra na documentação do README.
    """
    raise NotImplementedError("T1.1")
