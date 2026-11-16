"""Servidor HTTP unificado (Painel HTML, Relatórios Evidently, API JSON e /metrics).

Serve simultaneamente:
- `/` e `/monitoring/index.html` → Painel consolidado de saúde e alertas
- `/drift/*`, `/validation/*`, `/training/*` → Relatórios HTML/CSV/JSON em `reports/`
- `/metrics` → Endpoint OpenMetrics/Prometheus para scraping
- `/api/health` e `/api/alerts` → Endpoints JSON com estado de saúde e alertas
"""

from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import unquote, urlparse

from prometheus_client import CONTENT_TYPE_LATEST

from credit_risk.monitoring.prometheus_exporter import render_prometheus_metrics

if TYPE_CHECKING:
    import pandas as pd


def make_handler(
    health: pd.DataFrame,
    alerts: list[dict[str, Any]],
    reports_dir: Path,
) -> type[BaseHTTPRequestHandler]:
    """Cria a classe de handler HTTP configurada com os dados e diretório de relatórios."""
    prom_payload = render_prometheus_metrics(health, alerts).encode("utf-8")
    health_payload = json.dumps(
        health.to_dict(orient="records"), ensure_ascii=False, indent=2
    ).encode("utf-8")
    alerts_payload = json.dumps(alerts, ensure_ascii=False, indent=2).encode("utf-8")
    resolved_root = reports_dir.resolve()

    class ObservabilityHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            route = unquote(parsed.path)

            if route in {"", "/"}:
                self.send_response(HTTPStatus.FOUND)
                self.send_header("Location", "/monitoring/index.html")
                self.end_headers()
                return

            if route == "/metrics":
                self._send_bytes(prom_payload, CONTENT_TYPE_LATEST)
                return

            if route == "/api/health":
                self._send_bytes(health_payload, "application/json; charset=utf-8")
                return

            if route == "/api/alerts":
                self._send_bytes(alerts_payload, "application/json; charset=utf-8")
                return

            rel_path = route.lstrip("/")
            if rel_path.startswith("reports/"):
                rel_path = rel_path.removeprefix("reports/")

            target = (resolved_root / rel_path).resolve()
            if not str(target).startswith(str(resolved_root)) or not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "Recurso nao encontrado")
                return

            mime_type, _ = mimetypes.guess_type(str(target))
            content_type = mime_type or "application/octet-stream"
            if content_type.startswith("text/") or content_type == "application/json":
                content_type = f"{content_type}; charset=utf-8"
            self._send_bytes(target.read_bytes(), content_type)

        def _send_bytes(self, payload: bytes, content_type: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

    return ObservabilityHandler


def create_observability_server(
    health: pd.DataFrame,
    alerts: list[dict[str, Any]],
    reports_dir: Path,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> ThreadingHTTPServer:
    """Instancia o `ThreadingHTTPServer` do painel e métricas."""
    handler_cls = make_handler(health, alerts, reports_dir)
    return ThreadingHTTPServer((host, port), handler_cls)
