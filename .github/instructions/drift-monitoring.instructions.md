---
applyTo: "src/credit_risk/drift/**,src/credit_risk/monitoring/**,scripts/simulate_drift.py,scripts/detect_drift.py,scripts/monitor.py,scripts/predict.py"
description: Regras para simulação/detecção de drift e observabilidade (Etapas 2 e 3, 45% da nota)
---

# Drift (Etapa 2) e Observabilidade (Etapa 3)

Requisitos do enunciado ([00-tech-challenge.md](../../context/00-tech-challenge.md)):

## Simulação

- O dataset de Produção simula a **passagem do tempo** (ex.: janelas t1..tN com
  intensidade crescente).
- Alterar **≥ 2 features importantes** (de preferência as de maior importância no modelo).
- Simular **Data Drift** (mudança em P(X), ex.: inflação na renda, alta do desemprego)
  **e** **Concept Drift** (mudança em P(y|X), ex.: o mesmo perfil passa a ter mais
  default).
- Parâmetros da simulação explícitos e documentados, com seed fixa. Cada alteração deve
  ter uma **justificativa econômica** (alimenta a análise causal do README).

## Detecção

- Use **Evidently AI** para comparar Referência × Produção.
- Testes estatísticos explícitos por feature: **PSI** e **Kolmogorov-Smirnov**, calculados
  **pelo Evidently** (método `psi` e `ks`, sem reimplementar), com thresholds em `config.py` (PSI: < 0,1 estável; 0,1–0,25 atenção; > 0,25 drift).
- Gerar **relatório HTML** em `reports/` (versionado) apontando claramente as features com
  drift, além de JSON com as métricas para o monitoramento.
- Gerar predições no dataset de Produção e monitorar o prediction drift (distribuição do
  score).

## Observabilidade

- Logs de predição centralizados (JSONL/Parquet em `logs/`), **sem PII**, com: timestamp,
  janela, ID pseudonimizado, score, decisão, latência, versão do modelo.
- Métricas de saúde: volume, % de predições nulas/erro, % de lotes bloqueados pelo
  contrato, latência p50/p95, nº e share de features com drift, performance (AUC/KS)
  quando houver rótulo, alertas disparados.
- Saída: relatórios Evidently + painel HTML simples em `reports/monitoring/index.html`
  (métricas de saúde, alertas e links). Prometheus + Grafana só como extra.
