"""Testes do contrato de dados (Etapa 1). Implementar em T1.7."""

import pytest

pytestmark = pytest.mark.skip(reason="TODO(T1.7): implementar após T1.4–T1.6")


def test_reference_passes_contract() -> None:
    """A Referência limpa passa no schema de treino."""


def test_underage_is_blocked() -> None:
    """person_age < 18 → DataContractError."""


def test_null_income_is_blocked() -> None:
    """person_income nula → DataContractError."""


def test_duplicates_are_blocked() -> None:
    """Linhas duplicadas → DataContractError."""


def test_bad_batch_violates_every_rule() -> None:
    """O lote gerado por make_bad_batch viola TODAS as regras rígidas."""
