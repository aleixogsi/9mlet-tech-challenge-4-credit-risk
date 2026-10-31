# 📋 Plano do Projeto

> 🎯 **Projeto com 4 etapas · 4 integrantes**

## 👥 Responsáveis

| Etapa | Escopo | Responsável |
|---|---|---|
| **Etapa 1: Dados e contratos** | Preparação dos dados, contratos e baseline | Eduardo |
| **Etapa 2: Drift** | Simulação e detecção de Data/Concept Drift | Vini |
| **Etapa 3: Observabilidade** | Logs, métricas, alertas e painel | Fernando |
| **Etapa 4: Governança e entrega** | LGPD, documentação, vídeo e entrega | Vitor |

Cada etapa possui um único responsável. O status é controlado pelos checkboxes abaixo.

## 🧭 Etapa 1 · Dados, contratos e baseline · Eduardo

- [x] Automatizar o download e validar os nomes das colunas `T0.2`
- [x] Ler e limpar os dados `T1.1`
- [x] Separar Referência (treino) e Produção `T1.2`
- [ ] Proteger a branch `main` e criar o modelo de PR `T0.4`
- [x] Minimizar dados e pseudonimizar identificadores `T1.3`
- [x] Criar regras rígidas de qualidade `T1.4`
- [x] Bloquear dados inválidos e gerar relatório de falhas `T1.5`
- [x] Criar lote inválido demonstrável `T1.6`
- [x] Testar as regras do contrato `T1.7`
- [x] Treinar o baseline XGBoost usando somente a Referência `T1.8`
- [x] Medir a qualidade e listar as features importantes `T1.9`

### ✅ Artefatos concluídos

- [x] `data/raw/credit_risk_dataset.csv`
- [x] `data/reference/reference.parquet`
- [x] `data/production/production_base.parquet`
- [x] `data/bad_batches/bad_batch.parquet`
- [x] `reports/validation/bad_batch_failures.csv`
- [x] `reports/training/metrics.json`
- [x] `reports/training/feature_importance.csv`
- [x] `models/baseline_v1.joblib`
- [x] `tests/test_contracts.py`

## 🧭 Etapa 2 · Simulação e detecção de drift · Vini

- [ ] Criar dados sintéticos para testes `T0.5`
- [ ] Criar funções de alteração econômica dos dados `T2.2`
- [ ] Gerar janelas de produção t1–t5 com intensidade crescente `T2.3`
- [ ] Ajustar a simulação para alterar as features mais importantes `T2.1`
- [ ] Gerar predições das janelas simuladas `T2.4`
- [ ] Gerar relatórios Evidently com PSI e KS `T2.6`
- [ ] Escrever os testes da simulação e detecção `T2.7`

## 🧭 Etapa 3 · Observabilidade e monitoramento · Fernando

- [ ] Criar arquivos de exemplo para desenvolvimento do painel `T3.0`
- [ ] Criar o registro centralizado de predições sem PII `T3.1`
- [ ] Calcular métricas de saúde `T3.2`
- [ ] Criar alertas de degradação `T3.3`
- [ ] Montar o painel com métricas, alertas e links `T3.4`
- [ ] Fazer o painel ler os arquivos reais `T3.5`
- [ ] Documentar as métricas de saúde no README `T3.6`
- [ ] Gerar e versionar os relatórios e logs finais `T3.8`
- [ ] Implementar o extra Grafana + Prometheus, se adotado `T3.7`

## 🧭 Etapa 4 · Governança, documentação e entrega · Vitor

- [ ] Documentar o tratamento de dados pessoais no README `T4.1`
- [ ] Documentar base legal e retenção no README `T4.2`
- [ ] Gerar relatório de vieses e documentar a mitigação `T4.3`
- [ ] Documentar a análise causal da degradação `T4.4`
- [ ] Documentar como executar o projeto e consultar as evidências `T4.5`
- [ ] Escrever o roteiro do vídeo STAR `T4.6`
- [ ] Gravar o vídeo STAR com até 5 minutos `T4.7`
- [ ] Fazer a revisão final dos requisitos, README e vídeo `T4.8`
- [ ] Configurar testes automáticos em cada Pull Request `T0.6`

## 🎁 Tarefas concluídas de preparação

- [x] Ambiente Python configurado (`uv sync`) `T0.1`
- [x] Estrutura de pastas e arquivos do projeto
- [x] Configuração do Claude e do Copilot

## 📖 Glossário rápido

| Termo | O que é |
|---|---|
| **Referência** | Dados do passado usados para treinar o modelo |
| **Produção** | Dados atuais onde a economia pode ter mudado |
| **Drift** | Mudança dos dados atuais em relação aos dados de treino |
| **Data drift** | Mudança no perfil ou distribuição dos clientes |
| **Concept drift** | Mudança no comportamento para um mesmo perfil |
| **PSI / KS** | Testes estatísticos de mudança de distribuição |
| **Contrato de dados** | Regras que os dados precisam seguir para entrar no modelo |
| **Evidently** | Ferramenta de relatórios de drift |
| **PR** | Pull Request para integrar alterações ao projeto |
