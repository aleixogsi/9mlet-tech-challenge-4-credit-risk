"""Dados sintéticos com o mesmo schema do Credit Risk Dataset (T0.5).

Permitem desenvolver e testar as trilhas sem depender do dataset real
(ver context/05-interfaces.md, seção "Como não ficar travado"). Os DataFrames gerados
passam no contrato de treino (`build_training_schema`).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from credit_risk import config

HOME_OWNERSHIP = ["RENT", "OWN", "MORTGAGE", "OTHER"]
LOAN_INTENT = [
    "PERSONAL",
    "EDUCATION",
    "MEDICAL",
    "VENTURE",
    "HOMEIMPROVEMENT",
    "DEBTCONSOLIDATION",
]
LOAN_GRADE = ["A", "B", "C", "D", "E", "F", "G"]


def make_synthetic_credit_df(
    n: int = 1_000, seed: int = config.SEED, with_score: bool = False
) -> pd.DataFrame:
    """Gera `n` propostas sintéticas com `ID_COLUMN` + `FEATURES` + `TARGET`.

    O target depende da parcela sobre a renda, da taxa de juros e do grau do empréstimo,
    para que um modelo treinado nele aprenda algum sinal. Com `with_score=True`, adiciona
    uma coluna `score` (probabilidade de default) coerente com o target.
    """
    rng = np.random.default_rng(seed)
    age = rng.integers(config.MIN_AGE, 70, size=n).astype(float)
    income = np.clip(rng.lognormal(mean=10.9, sigma=0.5, size=n), 4_000, 2_000_000)
    loan_amnt = np.clip(rng.lognormal(mean=9.0, sigma=0.6, size=n), 500, 35_000).round()
    grade_idx = rng.choice(len(LOAN_GRADE), size=n, p=[0.32, 0.32, 0.2, 0.11, 0.03, 0.015, 0.005])
    int_rate = (7.0 + 2.2 * grade_idx + rng.normal(0, 1.0, size=n)).clip(5.0, 23.0).round(2)
    percent_income = (loan_amnt / income).round(2)
    frame = pd.DataFrame(
        {
            config.ID_COLUMN: [f"synthetic_{seed}_{i:08d}" for i in range(n)],
            "person_age": age,
            "person_income": income.round(),
            "person_emp_length": rng.integers(0, 20, size=n).astype(float),
            "loan_amnt": loan_amnt,
            "loan_int_rate": int_rate,
            "loan_percent_income": percent_income,
            "cb_person_cred_hist_length": rng.integers(2, 30, size=n).astype(float),
            "person_home_ownership": rng.choice(HOME_OWNERSHIP, size=n, p=[0.5, 0.08, 0.41, 0.01]),
            "loan_intent": rng.choice(LOAN_INTENT, size=n),
            "loan_grade": np.asarray(LOAN_GRADE)[grade_idx],
            "cb_person_default_on_file": rng.choice(["Y", "N"], size=n, p=[0.18, 0.82]),
        }
    )
    logit = -4.0 + 6.0 * percent_income + 0.15 * (int_rate - 11) + 0.3 * grade_idx
    probability = 1 / (1 + np.exp(-logit))
    frame[config.TARGET] = (rng.random(n) < probability).astype(int)
    if with_score:
        noise = rng.normal(0, 0.05, size=n)
        frame["score"] = np.clip(probability + noise, 0.0, 1.0)
    return frame


def make_synthetic_window(
    n: int = 1_000,
    seed: int = config.SEED,
    income_factor: float = 1.0,
    int_rate_shift: float = 0.0,
    with_score: bool = False,
) -> pd.DataFrame:
    """Gera uma janela de produção sintética, com drift controlado em renda e juros.

    `income_factor` multiplica `person_income` e `int_rate_shift` soma em `loan_int_rate`.
    Com os valores padrão, a janela tem a mesma distribuição de `make_synthetic_credit_df`.
    """
    frame = make_synthetic_credit_df(n=n, seed=seed, with_score=with_score)
    frame["person_income"] = (frame["person_income"] * income_factor).round()
    frame["loan_int_rate"] = (frame["loan_int_rate"] + int_rate_shift).round(2)
    return frame
