# Tech Challenge — Fase 4 (MLET / FIAP Pós Tech)

> **Fonte da verdade do projeto.** Transcrição fiel do enunciado oficial
> (`MLET - Tech Challenge - Fase 4.pdf`). Em caso de conflito entre este arquivo e
> qualquer outra documentação, decisão ou sugestão de IA, **este arquivo prevalece**.
> Não altere o conteúdo deste arquivo, exceto para corrigir erros de transcrição.

O Tech Challenge é o projeto da fase e reúne o conteúdo de todas as disciplinas dela.
É feito em grupo, é obrigatório e **vale 90% da nota de todas as disciplinas da fase**.

**Tema central:** Observabilidade Contínua, Detecção de Drift, Qualidade de Dados e
Governança em Produção.

## Contexto

Uma fintech de concessão de crédito possui um modelo de **Credit Scoring** rodando em
produção. Com mudanças recentes na economia (inflação, novos perfis de clientes), a
diretoria suspeita que o modelo está tomando decisões erradas e sofrendo
**degradação silenciosa**.

O foco do projeto é construir a camada de **Sustentação e Confiabilidade**. O grupo
deve:

- pegar um modelo de classificação simples;
- criar contratos de qualidade de dados;
- simular um cenário de degradação ao longo do tempo (**Data Drift** e **Concept Drift**);
- detectar essa mudança com ferramentas de observabilidade;
- garantir que todo o processo esteja documentado sob as regras de governança e
  privacidade (**LGPD**), incluindo uma **análise causal** do problema.

## Requisitos obrigatórios

### Repositório GitHub

- Pipeline de validação de dados (data contracts) configurado.
- Scripts para simulação e detecção estatística de Drift.
- Dashboards ou relatórios HTML gerados comprovando o monitoramento.
- Documentação consolidada de Governança no `README.md`.
- Histórico de commits semântico e organizado.

### Vídeo (5 minutos, método STAR)

- **Situation:** o risco da degradação silenciosa de modelos de crédito no mundo real.
- **Task:** requisitos técnicos da fase (interceptar dados ruins, detectar drift,
  garantir compliance).
- **Action:** ferramentas escolhidas de validação e observabilidade, simulação do drift
  e plano de governança.
- **Result:** demonstração prática do relatório apontando o drift, alertas gerados e
  lições aprendidas.

### Bibliotecas requeridas

- **Scikit-Learn / XGBoost**: treinar o modelo base de risco de crédito.
- **Great Expectations** ou **Pandera**: validação e qualidade de dados (Data Contracts).
- **Evidently AI** (ou Alibi Detect): detecção de Data/Concept Drift e geração de relatórios.
- Opcional (integração com a Fase 3): **Prometheus-client** para métricas.

### Boas práticas obrigatórias

- Separação clara entre o dataset de **Referência** (usado no treino) e o dataset de
  **Análise/Produção** (onde o drift ocorre).
- Pelo menos **3 regras rígidas** de qualidade de dados (ex.: sem nulos, range de
  idade, limites de renda).
- Relatório estatístico evidenciando a mudança de distribuição (ex.: teste **PSI** ou
  **Kolmogorov-Smirnov**).
- Documentação de compliance com **plano de privacidade (LGPD)**.

## Etapas de desenvolvimento

### Etapa 1: Validação de Dados e Contratos

*Disciplina: Validação de Dados e Bibliotecas de Qualidade.* Foco: garantir que lixo não
entre no modelo.

- Treinar um classificador base para o problema de crédito usando um dataset limpo
  (Dataset de Referência).
- Criar um contrato de dados (Great Expectations ou Pandera) com regras estritas
  (ex.: idade > 18, renda não pode ser nula, sem duplicatas).
- Forçar a passagem de um lote de dados com erros para demonstrar o contrato
  **falhando e bloqueando a ingestão**.
- **Entregável:** script de validação de dados operante e modelo baseline treinado.

### Etapa 2: Simulação e Detecção de Drift

*Disciplina: Data Drift.* Foco: diagnosticar a degradação do modelo ao longo do tempo.

- Criar um "Dataset de Produção" simulando a passagem do tempo, alterando
  intencionalmente a distribuição de **pelo menos duas variáveis importantes** (ex.:
  aumentar artificialmente a renda ou a taxa de desemprego dos clientes).
- Gerar predições para esse novo dataset.
- Usar o **Evidently AI** para comparar o Dataset de Referência com o Dataset de Produção.
- Identificar, por testes estatísticos (PSI, Kolmogorov-Smirnov etc.), quais features
  sofreram drift.
- **Entregável:** relatório de drift (HTML do Evidently ou painel customizado)
  apontando claramente as variáveis degradadas.

### Etapa 3: Observabilidade e Monitoramento

*Disciplina: Ferramentas de Monitoramento de Modelos.* Foco: visibilidade operacional
dos modelos.

- Centralizar os logs das predições e os resultados dos testes de drift da Etapa 2.
- Exportar as métricas para um dashboard interativo (Grafana + Prometheus) **ou**
  consolidar uma suíte de monitoramento completa em relatórios automatizados do Evidently.
- Documentar as métricas de saúde escolhidas (ex.: % de predições nulas, latência,
  volume e quantidade de alertas de drift).
- **Entregável:** dashboard ou conjunto de relatórios interativos evidenciando a saúde
  do sistema e os alertas de degradação.

### Etapa 4: Governança

*Disciplinas: Privacy By Design e By Default.* Foco: documentação arquitetural,
compliance e prescrição.

Tarefas teóricas, registradas no `README.md`:

- **Governança e LGPD:** plano de proteção de dados explicando como os dados sensíveis
  (PII) foram tratados no projeto, qual a **base legal** para a decisão de crédito e o
  **plano de retenção**.
- Gravar o vídeo STAR demonstrando o projeto.
- **Entregável:** documentação completa de Governança e **Causalidade** no README e link
  do vídeo.

## Critérios de avaliação

| Critério | Peso | Descrição |
|---|---|---|
| Validação de Dados | **25%** | Contratos de dados configurados corretamente (Great Expectations/Pandera) interceptando anomalias. |
| Detecção de Drift | **25%** | Simulação correta de alteração de distribuição e geração clara de relatório com Evidently AI. |
| Observabilidade e Logs | **20%** | Apresentação visual das métricas de saúde do modelo e dos alertas de drift (dashboard ou relatórios automatizados). |
| Governança (LGPD) | **15%** | Clareza na documentação sobre privacidade, base legal e mitigação de vieses. |
| Vídeo STAR | **15%** | Clareza na demonstração técnica da degradação do modelo e explicação do impacto (≤ 5 min). |

## Dataset sugerido

Datasets públicos tabulares focados em risco, crédito ou precificação, nos quais a
degradação econômica faça sentido prático.

Exemplos: German Credit Data (Kaggle/UCI), Home Credit Default Risk (Kaggle) ou
Lending Club Loan Data. **Qualquer dataset de classificação binária financeira com pelo
menos 5.000 amostras é aceito.**

> ⚠️ O German Credit Data (UCI) tem só 1.000 amostras e, sozinho, **não atende** ao
> mínimo de 5.000.

## Passo a passo resumido

1. **[Etapa 1]** Treinar o modelo base e escrever as regras de validação (Pandera/Great Expectations).
2. **[Etapa 2]** Alterar os dados de propósito para gerar drift e rodar os testes estatísticos com Evidently.
3. **[Etapa 3]** Consolidar os logs e expor relatórios visuais/dashboards de monitoramento.
4. **[Etapa 4]** Preencher a documentação de LGPD no README e gravar o vídeo.
