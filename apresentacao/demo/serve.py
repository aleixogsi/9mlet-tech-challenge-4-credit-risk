"""Servidor local da página de demonstração, com o modelo real respondendo ao vivo.

Serve os arquivos de apresentacao/demo/ e expõe:
- GET /api/status  → versão e AUC do modelo carregado;
- GET /api/predict?window=t1 → sorteia uma proposta da janela, passa pelo contrato de
  inferência, prediz com models/baseline_v1.joblib e devolve score, decisão, latência e o
  ID pseudonimizado (SHA-256 com salt). Alimenta a tabela da cena 1.
- GET /api/cliente?window=t1 → o celular sorteia um cliente da base de produção e aplica,
  na hora, as mudanças da janela descritas em configs/drift_scenarios.yaml, com as mesmas
  funções do simulate_drift.py. Com `silent=1`, o sorteio fica entre os casos de
  degradação silenciosa da janela: bons pagadores que caem na condição do concept drift e
  que o modelo aprova com risco baixo. O rótulo deles vira default, como acontece na
  simulação com a fração `fraction` desses clientes.
- GET /api/analisar?token=… → passa o cliente sorteado pelo contrato de inferência e pelo
  modelo e devolve a decisão e o que aconteceu depois (o rótulo da simulação).
- POST /api/contrato → roda o mesmo comando do terminal
  (`python scripts/validate_data.py --make-bad-batch`) e devolve a saída e o exit code.
  Alimenta o botão "Testar lote com erro" da cena 1 (D18).

Os sorteios da página não usam seed, então cada clique é um teste diferente. O pipeline
continua reprodutível com a seed 42. A finalidade MEDICAL fica fora do celular, porque a
D10 só a mostra em agregados. Nenhum dado pessoal sai das funções: o ID vai com hash.

Não deixa nada novo em logs/: os logs versionados são os da execução final (T3.8). O
comando do contrato grava uma linha em logs/validation.jsonl e regrava o relatório de falhas,
como no terminal; logo depois, os dois arquivos voltam ao conteúdo que tinham antes.

Uso (na raiz do repositório, depois de rodar o pipeline):
    uv run python apresentacao/demo/serve.py
    → http://127.0.0.1:8765/?cena=1
"""

from __future__ import annotations

import json
import logging
import math
import os
import random
import secrets
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import joblib
import pandas as pd
from pandera.errors import SchemaError, SchemaErrors

from credit_risk import config
from credit_risk.contracts.schemas import build_inference_schema
from credit_risk.data.privacy import pseudonymize_id
from credit_risk.drift.scenarios import apply_data_drift, load_scenarios
from credit_risk.inference import get_salt

HOST, PORT = "127.0.0.1", 8765
DEMO_DIR = Path(__file__).resolve().parent
logger = logging.getLogger("demo")

# Só para exibir no celular: os nomes das finalidades e as faixas do nível de risco.
INTENT_LABELS = {
    "EDUCATION": "Educação",
    "PERSONAL": "Pessoal",
    "VENTURE": "Negócio",
    "HOMEIMPROVEMENT": "Reforma",
    "DEBTCONSOLIDATION": "Quitar dívidas",
}
SENSITIVE_INTENTS = {"MEDICAL"}
LOW_RISK = 0.2
MAX_PENDING = 256
CONTRACT_COMMAND = ["scripts/validate_data.py", "--make-bad-batch"]
CONTRACT_TIMEOUT_S = 120
_contract_lock = threading.Lock()


def risk_level(score: float) -> str:
    """Faixa exibida no celular: Baixo < 0,2 ≤ Moderado < corte de aprovação ≤ Alto."""
    if score < LOW_RISK:
        return "Baixo"
    return "Moderado" if score < config.APPROVAL_THRESHOLD else "Alto"


def _number(value: Any, digits: int) -> float | None:
    value = float(value)
    return None if math.isnan(value) else round(value, digits)


class Engine:
    """Modelo, janelas e cenários de drift, carregados uma vez."""

    def __init__(self) -> None:
        self.model = joblib.load(config.MODEL_FILE)
        self.salt = get_salt()
        self.metrics = json.loads(
            (config.TRAINING_REPORTS_DIR / "metrics.json").read_text(encoding="utf-8")
        )
        self.schema = build_inference_schema()
        self.windows: dict[str, pd.DataFrame] = {}
        for name in ("t1", "t2", "t3", "t4", "t5"):
            path = config.PRODUCTION_DIR / f"{name}.parquet"
            if path.exists():
                frame = pd.read_parquet(path).drop(columns=[config.TARGET])
                self.windows[name] = self.schema.validate(frame)
        # Sem seed de propósito: na demonstração, cada sorteio é um teste diferente.
        self.rng = random.Random()
        self.lock = threading.Lock()
        base = pd.read_parquet(config.PRODUCTION_BASE_FILE)
        self.base = base[~base["loan_intent"].isin(SENSITIVE_INTENTS)].reset_index(drop=True)
        scenarios = load_scenarios(config.DRIFT_SCENARIOS_FILE)
        self.changes = {w["name"]: w.get("changes", []) for w in scenarios["windows"]}
        self.silent = {name: self._silent_pool(name) for name in self.changes}
        self.pending: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.model.predict_proba(self.base[config.FEATURES].head(1))

    # ---- tabela da cena 1 ----------------------------------------------------------
    def predict(self, window: str) -> dict:
        frame = self.windows[window]
        with self.lock:
            index = self.rng.randrange(len(frame))
        row = frame.iloc[[index]]
        start = time.perf_counter()
        score = float(self.model.predict_proba(row[config.FEATURES])[0, 1])
        latency = (time.perf_counter() - start) * 1000
        return {
            "record_id": pseudonymize_id(str(row[config.ID_COLUMN].iloc[0]), self.salt),
            "score": round(score, 4),
            "decision": "approved" if score < config.APPROVAL_THRESHOLD else "denied",
            "latency_ms": round(latency, 2),
            "window": window,
            "model_version": config.MODEL_VERSION,
        }

    # ---- celular -------------------------------------------------------------------
    def _drift(self, frame: pd.DataFrame, window: str) -> tuple[pd.DataFrame, dict | None]:
        """Aplica o data drift da janela; devolve também a regra de concept drift, se houver."""
        concept = None
        for change in self.changes[window]:
            if change["type"] == "data_drift":
                frame = apply_data_drift(frame, change)
            else:
                concept = change
        return frame, concept

    def _valid_rows(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Mantém só as linhas que passam no contrato de inferência."""
        try:
            self.schema.validate(frame.drop(columns=[config.TARGET]), lazy=True)
            return frame
        except SchemaErrors as exc:
            bad = exc.failure_cases["index"].dropna().unique()
            return frame.drop(index=bad, errors="ignore")

    def _silent_pool(self, window: str) -> dict | None:
        """Casos de degradação silenciosa: o modelo aprova com risco baixo e o rótulo vira 1."""
        frame, concept = self._drift(self.base, window)
        if concept is None or int(concept["flip_to"]) != 1:
            return None
        frame = self._valid_rows(frame)
        scores = self.model.predict_proba(frame[config.FEATURES])[:, 1]
        mask = (
            frame.eval(concept["condition"]).to_numpy(dtype=bool)
            & (frame[config.TARGET] == 0).to_numpy()
            & (scores < LOW_RISK)
        )
        rows = frame[mask].reset_index(drop=True)
        logger.info("Janela %s: %d casos de degradação silenciosa", window, len(rows))
        return {"rows": rows, "concept": concept}

    def new_client(self, window: str, silent: bool) -> dict:
        with self.lock:
            if silent:
                pool = self.silent.get(window)
                if not pool or pool["rows"].empty:
                    raise ValueError(f"a janela {window} não tem concept drift")
                concept = pool["concept"]
                row = pool["rows"].iloc[[self.rng.randrange(len(pool["rows"]))]].copy()
                before = int(row[config.TARGET].iloc[0])
                row[config.TARGET] = int(concept["flip_to"])
            else:
                row = self.base.iloc[[self.rng.randrange(len(self.base))]]
                row, concept = self._drift(row, window)
                before = int(row[config.TARGET].iloc[0])
                if concept is not None and self._flips(row, concept, before):
                    row = row.copy()
                    row[config.TARGET] = int(concept["flip_to"])
            token = secrets.token_hex(8)
            self.pending[token] = {
                "row": row,
                "window": window,
                "before": before,
                "after": int(row[config.TARGET].iloc[0]),
                "fraction": float(concept["fraction"]) if concept else None,
            }
            while len(self.pending) > MAX_PENDING:
                self.pending.popitem(last=False)
        r = row.iloc[0]
        return {
            "token": token,
            "window": window,
            "silent": silent,
            "profile": {
                "age": int(r["person_age"]),
                "income": _number(r["person_income"], 0),
                "emp_length": _number(r["person_emp_length"], 1),
                "amount": _number(r["loan_amnt"], 0),
                "int_rate": _number(r["loan_int_rate"], 2),
                "percent_income": _number(r["loan_percent_income"], 2),
                "intent": INTENT_LABELS.get(r["loan_intent"], str(r["loan_intent"]).title()),
            },
        }

    def _flips(self, row: pd.DataFrame, concept: dict, before: int) -> bool:
        """Mesma regra do concept drift da simulação, aplicada a um cliente só."""
        in_condition = bool(row.eval(concept["condition"]).iloc[0])
        return (
            in_condition
            and before != int(concept["flip_to"])
            and self.rng.random() < float(concept["fraction"])
        )

    def analyze(self, token: str) -> dict | None:
        with self.lock:
            item = self.pending.get(token)
        if item is None:
            return None
        outcome = {
            "defaulted": item["after"] == 1,
            "paid_before": item["before"] == 0,
            "concept_drift": item["after"] != item["before"],
            "fraction": item["fraction"],
        }
        base = {"window": item["window"], "model_version": config.MODEL_VERSION}
        try:
            valid = self.schema.validate(item["row"].drop(columns=[config.TARGET]))
        except (SchemaError, SchemaErrors) as exc:
            logger.info("Contrato bloqueou o cliente do celular: %s", type(exc).__name__)
            return {**base, "contract": "blocked", "decision": "blocked", "outcome": outcome}
        start = time.perf_counter()
        score = float(self.model.predict_proba(valid[config.FEATURES])[0, 1])
        latency = (time.perf_counter() - start) * 1000
        return {
            **base,
            "contract": "passed",
            "record_id": pseudonymize_id(str(valid[config.ID_COLUMN].iloc[0]), self.salt),
            "score": round(score, 4),
            "decision": "approved" if score < config.APPROVAL_THRESHOLD else "denied",
            "risk": risk_level(score),
            "latency_ms": round(latency, 2),
            "outcome": outcome,
        }


class Handler(SimpleHTTPRequestHandler):
    engine: Engine

    def do_GET(self) -> None:  # noqa: N802 (nome exigido pelo http.server)
        url = urlparse(self.path)
        query = parse_qs(url.query)
        window = query.get("window", ["t1"])[0]
        if url.path == "/api/status":
            self._json(
                {
                    "live": True,
                    "model_version": self.engine.metrics["model_version"],
                    "auc": self.engine.metrics["auc"],
                    "windows": list(self.engine.windows),
                }
            )
            return
        if url.path == "/api/predict":
            if window not in self.engine.windows:
                self._json({"error": f"janela desconhecida: {window}"}, status=400)
                return
            self._json(self.engine.predict(window))
            return
        if url.path == "/api/cliente":
            if window not in self.engine.changes:
                self._json({"error": f"janela desconhecida: {window}"}, status=400)
                return
            try:
                silent = query.get("silent", ["0"])[0] == "1"
                self._json(self.engine.new_client(window, silent))
            except ValueError as exc:
                self._json({"error": str(exc)}, status=400)
            return
        if url.path == "/api/analisar":
            result = self.engine.analyze(query.get("token", [""])[0])
            if result is None:
                self._json({"error": "cliente expirado; atualize os dados"}, status=404)
                return
            self._json(result)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 (nome exigido pelo http.server)
        if urlparse(self.path).path != "/api/contrato":
            self._json({"error": "rota desconhecida"}, status=404)
            return
        try:
            self._json(run_contract_demo())
        except (OSError, subprocess.SubprocessError) as exc:
            logger.exception("Falha ao rodar o contrato")
            self._json({"error": str(exc)}, status=500)

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        if "/api/" not in self.path:
            logger.info(format, *args)


def _last_record(path: Path, batch_name: str) -> dict[str, Any] | None:
    if not path.exists():
        return None
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return next((r for r in reversed(records) if r.get("batch_name") == batch_name), None)


def run_contract_demo() -> dict[str, Any]:
    """Roda `validate_data.py --make-bad-batch`, o mesmo comando do terminal, e devolve a saída.

    O script gera o lote com erros, valida pelo contrato e sai com exit code 1. Ele grava uma
    linha em logs/validation.jsonl e regrava o relatório de falhas; depois da execução, os
    dois arquivos voltam ao conteúdo de antes. Sem salt no ambiente, usa um salt aleatório
    só para essa execução (o relatório é descartado de qualquer forma).
    """
    tracked = [config.VALIDATION_LOG, config.VALIDATION_REPORTS_DIR / "bad_batch_failures.csv"]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    env.setdefault(config.PSEUDONYMIZATION_SALT_ENV, secrets.token_hex(16))
    with _contract_lock:
        saved = {path: path.read_bytes() if path.exists() else None for path in tracked}
        started = time.perf_counter()
        try:
            proc = subprocess.run(
                [sys.executable, *CONTRACT_COMMAND],
                cwd=config.ROOT_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=CONTRACT_TIMEOUT_S,
                check=False,
            )
            elapsed_ms = (time.perf_counter() - started) * 1000
            record = _last_record(config.VALIDATION_LOG, "bad_batch")
        finally:
            for path, content in saved.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(content)
    return {
        "command": "python " + " ".join(CONTRACT_COMMAND),
        "lines": [line for line in proc.stdout.splitlines() if line.strip()],
        "exit_code": proc.returncode,
        "elapsed_ms": round(elapsed_ms),
        "record": record,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    Handler.engine = Engine()
    server = ThreadingHTTPServer((HOST, PORT), partial(Handler, directory=str(DEMO_DIR)))
    logger.info("Página ao vivo em http://%s:%d/?cena=1 (Ctrl+C para sair)", HOST, PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
