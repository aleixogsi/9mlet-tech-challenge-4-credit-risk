"""Testes de simulação e detecção de drift (Etapa 2). Implementar em T2.7."""

import pytest

pytestmark = pytest.mark.skip(reason="TODO(T2.7): implementar após T2.2, T2.3 e T2.6")


def test_scale_scenario_changes_feature() -> None:
    """op=scale altera a média na proporção esperada."""


def test_concept_drift_changes_only_target() -> None:
    """Concept drift altera loan_status e mantém as features."""


def test_windows_are_reproducible() -> None:
    """Mesma seed → mesmas janelas."""


def test_identical_data_has_no_drift() -> None:
    """Referência × ela mesma → nenhuma feature com status 'drift'."""


def test_shifted_feature_is_flagged() -> None:
    """Feature fortemente deslocada → status 'drift' na drift_table (PSI e KS)."""
