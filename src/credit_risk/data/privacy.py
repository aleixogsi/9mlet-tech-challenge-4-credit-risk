"""Privacy by Design/Default (LGPD): minimização e pseudonimização."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def minimize_columns(df: pd.DataFrame, allowed: list[str]) -> pd.DataFrame:
    """Mantém apenas as colunas necessárias à finalidade (princípio da necessidade).

    TODO(T1.3): descartar qualquer coluna fora de `allowed` e logar quais foram removidas.
    """
    raise NotImplementedError("T1.3")


def pseudonymize_id(value: str, salt: str) -> str:
    """Gera um identificador pseudonimizado (hash com salt) para rastrear predições sem PII.

    TODO(T1.3): SHA-256 de salt + value. O salt vem do .env (PSEUDONYMIZATION_SALT).
    """
    raise NotImplementedError("T1.3")
