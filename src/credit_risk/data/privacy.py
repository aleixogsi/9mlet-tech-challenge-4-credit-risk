"""Privacy by Design/Default (LGPD): minimização e pseudonimização."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def minimize_columns(df: pd.DataFrame, allowed: list[str]) -> pd.DataFrame:
    """Mantém apenas as colunas necessárias à finalidade (princípio da necessidade).

    A operação falha explicitamente se uma coluna autorizada não existir.
    """
    missing = sorted(set(allowed) - set(df.columns))
    if missing:
        raise ValueError(f"Colunas autorizadas ausentes: {missing}")
    return df.loc[:, allowed].copy()


def pseudonymize_id(value: str, salt: str) -> str:
    """Gera um identificador pseudonimizado (hash com salt) para rastrear predições sem PII.

    O resultado não permite recuperar o identificador original sem o salt.
    """
    import hashlib

    return hashlib.sha256(f"{salt}{value}".encode()).hexdigest()
