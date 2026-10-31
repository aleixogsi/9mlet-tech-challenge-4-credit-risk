"""Painel HTML de monitoramento (entregável da Etapa 3).

Mantido simples de propósito: uma página que reúne o que o enunciado pede (métricas de
saúde e alertas de drift) e aponta para os relatórios do Evidently.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def build_dashboard(health: pd.DataFrame, alerts: list[dict[str, Any]], output_html: Path) -> Path:
    """Gera reports/monitoring/index.html.

    TODO(T3.4): três blocos: (1) tabela de métricas de saúde por janela, com destaque para
    as que passaram do threshold; (2) tabela de alertas; (3) links para os HTMLs do
    Evidently em reports/drift/ e para o relatório de validação. Gráficos são opcionais.
    """
    raise NotImplementedError("T3.4")
