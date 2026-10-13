# Checklist de entregáveis

Cada item vem de [00-tech-challenge.md](00-tech-challenge.md). Marque `[x]` quando o item
estiver **implementado e evidenciado no repositório** (código + artefato/relatório).
O peso entre parênteses é o do critério de avaliação.

## Etapa 1: Validação de Dados (25%)

- [ ] Dataset financeiro binário com **≥ 5.000 amostras** escolhido e documentado
- [ ] Dataset de **Referência** separado do de **Produção** (arquivos/pastas distintos)
- [ ] Classificador baseline treinado (Scikit-Learn/XGBoost) com métricas registradas
- [ ] Contrato de dados em **Pandera ou Great Expectations**
- [ ] **≥ 3 regras rígidas** (ex.: idade > 18, renda não nula, sem duplicatas)
- [ ] Lote com erros forçado → contrato **falha e bloqueia a ingestão** (demonstrável)
- [ ] Script de validação operante (entregável)

## Etapa 2: Detecção de Drift (25%)

- [ ] "Dataset de Produção" simulando a passagem do tempo
- [ ] Distribuição alterada em **≥ 2 variáveis importantes**
- [ ] Simulação de **Data Drift** (P(X))
- [ ] Simulação de **Concept Drift** (P(y|X))
- [ ] Predições geradas para o dataset de Produção
- [ ] Comparação Referência × Produção com **Evidently AI**
- [ ] Testes estatísticos (**PSI** e/ou **Kolmogorov-Smirnov**) por feature
- [ ] **Relatório HTML** apontando claramente as variáveis degradadas

## Etapa 3: Observabilidade e Logs (20%)

- [ ] Logs de predição centralizados
- [ ] Resultados dos testes de drift centralizados
- [ ] Dashboard (Grafana + Prometheus) **ou** suíte de relatórios automatizados do Evidently
- [ ] Métricas de saúde documentadas (% predições nulas, latência, volume, nº de alertas de drift)
- [ ] Alertas de degradação visíveis no dashboard/relatório

## Etapa 4: Governança LGPD (15%), no `README.md`

- [ ] Plano de proteção de dados: como a **PII** foi tratada
- [ ] **Base legal** para a decisão de crédito
- [ ] **Plano de retenção** de dados
- [ ] **Mitigação de vieses**
- [ ] **Análise causal** da degradação (causalidade)

## Vídeo STAR (15%)

- [ ] ≤ 5 minutos
- [ ] Situation: risco da degradação silenciosa
- [ ] Task: interceptar dados ruins, detectar drift, garantir compliance
- [ ] Action: ferramentas de validação/observabilidade, simulação de drift, plano de governança
- [ ] Result: demo do relatório apontando o drift, alertas e lições aprendidas
- [ ] Link do vídeo no README

## Repositório

- [ ] Pipeline de validação de dados configurado
- [ ] Scripts de simulação e detecção de drift
- [ ] Relatórios HTML gerados e versionados
- [ ] Governança consolidada no `README.md`
- [ ] Histórico de commits semântico e organizado
