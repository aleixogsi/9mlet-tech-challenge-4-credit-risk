"""Detecção de drift com Evidently AI: Referência × Produção.

Os testes estatísticos exigidos pelo enunciado (PSI e Kolmogorov-Smirnov) são calculados
pelo próprio Evidently, configurando o método de drift (`stattest`/`method`) como "psi"
e "ks". Não reimplementamos as estatísticas.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def build_drift_report(
    reference: pd.DataFrame, current: pd.DataFrame, output_html: Path
) -> dict[str, Any]:
    """Gera o HTML do Evidently (data drift + prediction drift) e retorna as métricas em dict.

    TODO(T2.6): API do Evidently 0.7 (`from evidently import Report`,
    `from evidently.presets import DataDriftPreset`), versão fixada no uv.lock.
    Rodar o drift por feature com PSI e com KS. O HTML precisa apontar claramente as
    features com drift (entregável da Etapa 2).
    """
    raise NotImplementedError("T2.6")


def drift_table(report_metrics: dict[str, Any]) -> pd.DataFrame:
    """Extrai das métricas do Evidently uma tabela por feature.

    Colunas: feature, psi, ks_pvalue, status (stable/warning/drift), drift_detected.
    Alimenta o `drift_summary.json` (formato em context/05-interfaces.md, seção 4).

    TODO(T2.6): status segundo config.PSI_WARNING / config.PSI_DRIFT.
    """
    raise NotImplementedError("T2.6")


def build_performance_report(
    reference: pd.DataFrame, current: pd.DataFrame, output_html: Path
) -> dict[str, Any]:
    """Relatório de classificação (com rótulo) para evidenciar o concept drift.

    TODO(T2.6)
    """
    raise NotImplementedError("T2.6")
