# Checklist de entregáveis

Cada item vem de [00-tech-challenge.md](00-tech-challenge.md). Marque `[x]` quando o item
estiver **implementado e evidenciado no repositório** (código + artefato/relatório).
O peso entre parênteses é o do critério de avaliação.

## Etapa 1: Validação de Dados (25%)

- [x] Dataset financeiro binário com **≥ 5.000 amostras** escolhido e documentado
- [x] Dataset de **Referência** separado do de **Produção** (arquivos/pastas distintos)
- [x] Classificador baseline treinado (Scikit-Learn/XGBoost) com métricas registradas
- [x] Contrato de dados em **Pandera ou Great Expectations**
- [x] **≥ 3 regras rígidas** (ex.: idade > 18, renda não nula, sem duplicatas)
- [x] Lote com erros forçado → contrato **falha e bloqueia a ingestão** (demonstrável)
- [x] Script de validação operante (entregável)

## Etapa 2: Detecção de Drift (25%)

- [x] "Dataset de Produção" simulando a passagem do tempo
- [x] Distribuição alterada em **≥ 2 variáveis importantes**
- [x] Simulação de **Data Drift** (P(X))
- [x] Simulação de **Concept Drift** (P(y|X))
- [x] Predições geradas para o dataset de Produção
- [x] Comparação Referência × Produção com **Evidently AI**
- [x] Testes estatísticos (**PSI** e/ou **Kolmogorov-Smirnov**) por feature
- [x] **Relatório HTML** apontando claramente as variáveis degradadas

## Etapa 3: Observabilidade e Logs (20%)

- [x] Logs de predição centralizados
- [x] Resultados dos testes de drift centralizados
- [x] Dashboard (Grafana + Prometheus) **ou** suíte de relatórios automatizados do Evidently
- [x] Métricas de saúde documentadas (% predições nulas, latência, volume, nº de alertas de drift)
- [x] Alertas de degradação visíveis no dashboard/relatório

## Etapa 4: Governança LGPD (15%), no `README.md`

- [x] Plano de proteção de dados: como a **PII** foi tratada
- [x] **Base legal** para a decisão de crédito
- [x] **Plano de retenção** de dados
- [x] **Mitigação de vieses**
- [x] **Análise causal** da degradação (causalidade)

## Vídeo STAR (15%)

Roteiro em `docs/roteiro-video-star.md` (T4.6). Vídeo gravado e publicado em https://youtu.be/efrBXjaSIYo (T4.7).

- [x] ≤ 5 minutos (4:52)
- [x] Situation: risco da degradação silenciosa
- [x] Task: interceptar dados ruins, detectar drift, garantir compliance
- [x] Action: ferramentas de validação/observabilidade, simulação de drift, plano de governança
- [x] Result: demo do relatório apontando o drift, alertas e lições aprendidas
- [x] Link do vídeo no README

## Repositório

- [x] Pipeline de validação de dados configurado
- [x] Scripts de simulação e detecção de drift
- [x] Relatórios HTML gerados e versionados
- [x] Governança consolidada no `README.md`
- [x] Histórico de commits semântico e organizado
