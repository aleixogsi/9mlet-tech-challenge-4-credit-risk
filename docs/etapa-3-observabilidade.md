# 🔭 Guia Simplificado da Etapa 3: Observabilidade e Monitoramento

Este documento explica, de forma direta e acessível, tudo o que foi construído na **Etapa 3 (Observabilidade e Logs — 20% da nota)** do Tech Challenge Fase 4.

---

## 1. Qual problema a Etapa 3 resolve?

Na **Etapa 1**, garantimos que dados corrompidos ou fora do contrato não entrem no modelo (Pandera).
Na **Etapa 2**, simulamos a deterioração da economia ao longo de 5 janelas de tempo (`t1` a `t5`) e medimos estatisticamente o *Data Drift* e o *Concept Drift* (Evidently AI).

Porém, em um ambiente real de produção, ninguém abre dezenas de arquivos CSV, JSON e HTML manualmente todos os dias para descobrir se o modelo quebrou. **A Etapa 3 constrói o "painel de comando" (Observabilidade) do modelo de crédito**, respondendo automaticamente a três perguntas:

1. **O pipeline e a infraestrutura estão saudáveis?** (Quantas propostas entraram? Algum lote foi bloqueado pelo contrato? Há predições dando erro/nulo? A latência está rápida?)
2. **O comportamento das entradas ou dos scores mudou?** (Quantas variáveis sofreram drift? O modelo está negando muito mais crédito do que antes?)
3. **O modelo perdeu qualidade e precisa de ação imediata?** (Quais alertas críticos ou de atenção dispararam em cada janela?)

---

## 2. Como os dados fluem na Etapa 3?

```text
┌────────────────────────────┐   ┌────────────────────────────┐   ┌────────────────────────────────┐
│   logs/validation.jsonl    │   │   logs/predictions.jsonl   │   │ reports/drift/drift_summary.json│
│ (Lotes aprovados/bloqueados│   │ (25.000 predições sem PII, │   │ (PSI, KS, Score Drift e AUC/KS │
│  pelo contrato Pandera)    │   │  com hash SHA-256 + salt)  │   │  calculados pelo Evidently AI) │
└─────────────┬──────────────┘   └─────────────┬──────────────┘   └───────────────┬────────────────┘
              │                                │                                  │
              └────────────────────────────────┼──────────────────────────────────┘
                                               ▼
                              ┌─────────────────────────────────┐
                              │  1. Saúde por Janela (health.py)│
                              │     compute_health()            │
                              └────────────────┬────────────────┘
                                               ▼
                              ┌─────────────────────────────────┐
                              │  2. Regras de Alerta (alerts.py)│
                              │     evaluate_alerts()           │
                              │     ─► logs/alerts.jsonl        │
                              └────────────────┬────────────────┘
                                               ▼
              ┌────────────────────────────────┴────────────────────────────────┐
              ▼                                                                 ▼
┌───────────────────────────────────────────┐     ┌─────────────────────────────────────────────┐
│ 3A. Painel HTML + Servidor HTTP Unificado │     │ 3B. Exportador Prometheus + Grafana (Docker)│
│ • reports/monitoring/index.html           │     │ • reports/monitoring/metrics.prom           │
│ • http://localhost:8000/                  │     │ • http://localhost:8000/metrics             │
│ • http://localhost:8000/api/health        │     │ • Prometheus (http://localhost:9090)        │
│ • http://localhost:8000/api/alerts        │     │ • Grafana    (http://localhost:3000)        │
└───────────────────────────────────────────┘     └─────────────────────────────────────────────┘
```

---

## 3. O que foi construído em cada tarefa (`T3.0` a `T3.8`)

### 🧩 `T3.0` — Mocks de interface para testes rápidos (`tests/fixtures/mocks/`)
- **O que é:** Arquivos pequenos de exemplo (`predictions.jsonl`, `validation.jsonl` e `drift_summary.json`) que imitam exatamente o formato oficial do projeto.
- **Por que fizemos:** Permitem testar todos os cálculos de saúde, alertas, painel HTML e servidor Prometheus em **menos de 2 segundos** com `pytest`, sem precisar rodar o treinamento e o Evidently toda vez.

---

### 🔒 `T3.1` — Registro centralizado de predições sem PII (`src/credit_risk/monitoring/prediction_logger.py`)
- **O que é:** O guardião do arquivo `logs/predictions.jsonl` (funções `log_predictions` e `read_predictions`).
- **Como funciona na prática:**
  - Toda vez que o modelo faz uma predição em `scripts/predict.py`, ele passa os registros por `log_predictions`.
  - O logger **valida linha por linha** se existem apenas os 7 campos permitidos: `timestamp`, `window`, `record_id`, `score`, `decision`, `latency_ms` e `model_version`.
  - **Proteção LGPD (Privacy by Design):** Se alguém tentar gravar um campo extra (como `cpf`, `nome` ou `application_id` original) ou se o `record_id` não for um hash SHA-256 hexadecimal de 64 caracteres, o logger **bloqueia a gravação imediatamente com erro (`ValueError`)**.

---

### 🩺 `T3.2` — Cálculo das métricas de saúde (`src/credit_risk/monitoring/health.py`)
- **O que é:** A função `compute_health(predictions, validation_log, drift_results)` cruza as três fontes de dados e devolve uma tabela consolidada com **uma linha por janela (`t1` a `t5`)**.
- **O que cada métrica significa (em português claro):**
  - **Saúde Operacional:**
    - `volume`: quantas propostas foram avaliadas na janela (`5.000` por janela).
    - `null_predictions_pct`: porcentagem de predições que falharam (`score = null` / `decision = error`).
    - `blocked_batches_pct`: porcentagem de lotes barrados pelo contrato de qualidade Pandera.
    - `latency_p50_ms` e `latency_p95_ms`: tempo mediano (`p50`) e tempo nos 5% casos mais lentos (`p95`) para o modelo responder, em milissegundos (fica em torno de `~4,5 ms` a `5,1 ms`).
  - **Prediction Drift (Mudança nas decisões do modelo):**
    - `mean_score`: risco médio de calote previsto pelo modelo (sobe de `0,214` em `t1` para `0,429` em `t5`).
    - `approval_rate`: taxa de clientes aprovados (cai de `84,1%` em `t1` para `61,0%` em `t5` conforme a crise avança).
    - `prediction_psi`: índice estatístico PSI que mede o quanto a distribuição dos scores mudou em relação à Referência.
  - **Data Drift (Mudança no perfil dos clientes):**
    - `n_drifted` e `share_drifted`: quantas (e qual `%`) das 11 variáveis de entrada mudaram de distribuição.
    - `drifted_features`: lista exata dos nomes das colunas que sofreram drift na janela.
  - **Performance / Concept Drift (Queda real da qualidade após chegar o rótulo):**
    - `auc`, `ks` e `gini`: métricas clássicas de poder de separação entre bons e maus pagadores.
    - `auc_drop`: quanto a `AUC` caiu em relação à Referência (`0,941`).

---

### 🚨 `T3.3` — Motor de alertas de degradação (`src/credit_risk/monitoring/alerts.py`)
- **O que é:** A função `evaluate_alerts(health)` aplica as regras de negócio definidas em `src/credit_risk/config.py` e `write_alerts()` salva todos os alertas disparados em `logs/alerts.jsonl`.
- **As 6 regras monitoradas:**
  1. `contract_blocked` (`critical`): qualquer lote bloqueado pelo Pandera (`blocked_batches_pct > 0` ou `bad_batch`).
  2. `data_drift` (`critical`): quando **30% ou mais** das features sofrem drift (`share_drifted >= 0.30`).
  3. `prediction_drift` (`warning` / `critical`): quando o PSI do score passa de `0,10` (atenção) ou de `0,25` (crítico).
  4. `performance_drop` (`warning` / `critical`): quando a AUC cai mais de `0,05` (`5 pontos percentuais`) em relação à referência.
  5. `null_predictions` (`warning` / `critical`): quando mais de `1%` das predições retornam erro/nulo.
  6. `latency` (`warning` / `critical`): quando a latência `p95` ultrapassa `200 ms`.
- **A história que os alertas contam de `t1` a `t5`:**
  - **`bad_batch`**: dispara `contract_blocked` (`CRITICAL`) provando que dados sujos foram barrados na porta.
  - **`t1` e `t2`**: **0 alertas**. A inflação inicial em `t2` ainda é absorvida sem degradar o modelo.
  - **`t3`**: dispara `prediction_drift` (`WARNING`, PSI = `0,224`). **Destaque importante para o vídeo:** em `t3`, ainda não há *concept drift* e a queda de AUC (`-0,050`) ainda não cruzou o limite, mas o alerta de *Prediction Drift* já avisa a equipe precocemente que os scores estão subindo!
  - **`t4` e `t5`**: disparam a tríade `data_drift` (`CRITICAL`, 36% das features), `prediction_drift` (`CRITICAL`, PSI > 0,62) e `performance_drop` (`WARNING` em `t4` com `-0,099` de AUC e `CRITICAL` em `t5` com `-0,140` de AUC), comprovando a degradação severa do modelo.

---

### 🖥️ `T3.4`, `T3.5` e `T3.6` — Painel HTML e Script Integrador (`dashboard.py` e `scripts/monitor.py`)
- **O que é:** O gerador `build_dashboard()` cria `reports/monitoring/index.html`, uma página web limpa e responsiva com:
  1. **4 Cards de KPIs no topo** (5 janelas / 25.000 predições, 8 alertas disparados, pico de 36,4% de data drift e menor AUC de 0,801).
  2. **Tabela 1 — Saúde por Janela**, colorindo automaticamente cada célula de verde (`OK`), amarelo (`WARNING`) ou vermelho (`CRITICAL`).
  3. **Tabela 2 — Alertas Disparados**, detalhando severidade, métrica, valor observado vs. limite e mensagem explicativa.
  4. **Seção 3 — Central de Evidências**, com links clicáveis para todos os relatórios HTML do Evidently (`drift_t1..t5.html` e `performance_t1..t5.html`), tabelas `psi_ks_t1..t5.csv` e falhas do lote bloqueado (`bad_batch_failures.csv`).

---

### 🐳 `T3.7` — Servidor HTTP Unificado, Prometheus, Grafana e Docker
Para ir além do HTML estático, implementamos uma arquitetura completa de observabilidade servida tanto localmente quanto via containers Docker:

1. **Exportador Prometheus (`src/credit_risk/monitoring/prometheus_exporter.py`)**:
   - Converte todas as métricas de saúde e contagens de alertas em *Gauges* oficiais do Prometheus (`credit_risk_share_drifted`, `credit_risk_auc`, `credit_risk_prediction_psi`, `credit_risk_alerts_total` etc.).
2. **Servidor HTTP Unificado (`src/credit_risk/monitoring/server.py`)**:
   - Ao rodar `python scripts/monitor.py --serve --port 8000`, um único servidor Python entrega:
     - `http://localhost:8000/` → Painel HTML e todos os relatórios interativos do Evidently;
     - `http://localhost:8000/metrics` → Endpoint para o Prometheus coletar as métricas;
     - `http://localhost:8000/api/health` e `/api/alerts` → API JSON.
3. **`Dockerfile` + `docker-compose.yml` com Auto-Provisioning**:
   - Com um único comando (`docker compose up --build -d`), sobem 3 containers:
     - `credit-risk-monitor` (`:8000`): servidor Python do projeto;
     - `credit-risk-prometheus` (`:9090`): coleta `monitor:8000/metrics` a cada 5 segundos;
     - `credit-risk-grafana` (`:3000`): já sobe com a fonte de dados do Prometheus e o dashboard **Credit Risk — Observabilidade, Drift e Saúde** configurados automaticamente como tela inicial!

---

## 4. Cola Rápida de Comandos (Para Testes e Vídeo STAR)

### Rodar todos os testes automatizados da Etapa 3:
```powershell
.\.venv\Scripts\pytest.exe tests/test_monitoring.py
```

### Rodar todos os 118 testes do projeto inteiro:
```powershell
.\.venv\Scripts\pytest.exe
```

### Atualizar relatórios/logs e subir o servidor local (sem Docker):
```powershell
.\.venv\Scripts\python.exe scripts/monitor.py --serve --port 8000
```
- Acesse `http://localhost:8000` para navegar pelo Painel HTML e pelos relatórios do Evidently.

### Subir a stack completa com Docker (Monitor + Prometheus + Grafana):
```powershell
docker compose up --build -d
```
- **Painel Web + Relatórios Evidently**: `http://localhost:8000`
- **Grafana (Dashboard pronto na Home)**: `http://localhost:3000`
- **Prometheus**: `http://localhost:9090`
- Para desligar: `docker compose down`
