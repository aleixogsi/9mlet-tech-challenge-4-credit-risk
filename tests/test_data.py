"""Testes da limpeza dos dados brutos (Etapa 1)."""

import pandas as pd

from credit_risk import config
from credit_risk.data.clean import clean
from tests.fixtures.synthetic import make_synthetic_credit_df


def test_clean_removes_duplicates_with_different_ids() -> None:
    frame = make_synthetic_credit_df(n=50, seed=11)[
        [config.ID_COLUMN, *config.FEATURES, config.TARGET]
    ]
    copy = frame.iloc[[0]].copy()
    copy[config.ID_COLUMN] = "application_99999999"
    with_duplicate = pd.concat([frame, copy], ignore_index=True)

    cleaned = clean(with_duplicate)

    content = [*config.FEATURES, config.TARGET]
    assert not cleaned.duplicated(subset=content).any()
    assert len(cleaned) == len(clean(frame))
