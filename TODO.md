# 📋 Plano do Projeto

> 🎯 **Entrega final: terça, 17/11** · São 5 semanas · 4 pessoas

---

## 👥 Quem faz o quê

Cada pessoa cuida de **uma parte** do projeto do começo ao fim.

| | Parte | Em uma frase | Nome |
|---|---|---|---|
| 🟦 | **A: Dados** | Prepara os dados e cria as regras que barram dados ruins | |
| 🟩 | **B: Modelo** | Treina o modelo de crédito e faz as previsões | |
| 🟨 | **C: Drift** | Simula a economia mudando e detecta quando os dados mudaram | |
| 🟥 | **D: Painel** | Monta o painel de saúde do modelo e os alertas | |

A carga de trabalho é parecida para todos.

---

## 📅 As 5 semanas

| Semana | Datas | Objetivo |
|---|---|---|
| **1** | 13/10 → 19/10 | 🧱 Preparar a base |
| **2** | 20/10 → 26/10 | ⚙️ Construir o principal de cada parte |
| **3** | 27/10 → 02/11 | 🔗 Juntar as partes |
| **4** | 03/11 → 09/11 | 🧪 Testar tudo junto e escrever o README |
| **5** | 10/11 → 17/11 | 🎬 Gravar o vídeo e entregar |

**Toda segunda-feira** a gente confere se a semana foi concluída (reunião de 30 min).

---

## 🤝 Como trabalhar sem ficar esperando o colega

1. **Não espere ninguém.** Se a sua tarefa precisa de algo que o colega ainda não fez,
   use os **dados de mentira** que vamos criar na semana 1. Eles têm o mesmo formato dos
   dados reais. Quando a parte do colega ficar pronta, é só trocar.
2. **⚠️ = alguém precisa disso.** Tarefas com ⚠️ têm data limite porque outra pessoa
   depende delas. Faça essas **primeiro**.
3. **Não mude formatos combinados sozinho.** O formato dos arquivos que passam de uma
   pessoa para outra está em [context/05-interfaces.md](context/05-interfaces.md). Quer
   mudar? Avise o grupo antes.
4. **Cada um mexe só na sua parte.** No README, cada um escreve só a sua seção. Assim
   não dá conflito no git.
5. **Revisão em rodízio:** A revisa B · B revisa C · C revisa D · D revisa A. Tente revisar em até 1 dia.

**Passo a passo de cada tarefa:**
crie uma branch → faça a tarefa → abra o PR → colega revisa → merge → marque ✅ aqui.

> 💡 O código (ex.: `T1.4`) serve para achar a tarefa no projeto. Busque por `TODO(T1.4)`
> e você cai direto no arquivo certo.

---

## 🧱 Semana 1 · 13/10 → 19/10 · Preparar a base

**Ao final da semana:** dados reais baixados, dados de mentira prontos, cada um com a
primeira tarefa entregue.

### 🟦 A: Dados
- [ ] ⚠️ **até qui 15/10**: Baixar o dataset do Kaggle e conferir os nomes das colunas. Se a licença permitir, colocar o arquivo no git (assim o avaliador roda sem conta no Kaggle) `T0.2`
- [ ] Ler e limpar os dados (tirar vazios, idades e rendas absurdas, linhas repetidas) `T1.1`
- [ ] ⚠️ **até seg 19/10**: Separar os dados em **Referência** (treino) e **Produção** `T1.2`

### 🟩 B: Modelo
- [ ] Proteger a branch `main` no GitHub e criar o modelo de PR `T0.4`
- [ ] Criar o **registro das previsões** (log, sem dados pessoais) `T3.1`
- [ ] Esconder os dados pessoais (trocar o ID por um código) `T1.3`

### 🟨 C: Drift
- [ ] ⚠️ **até qui 15/10**: Criar o gerador de **dados de mentira** para o time testar `T0.5`
- [ ] Criar as funções que **alteram os dados** para simular a economia mudando `T2.2`

> Nada disso depende de ninguém: dá para testar com números aleatórios.

### 🟥 D: Painel
- [ ] ⚠️ **até qua 14/10**: Criar **arquivos de exemplo** (logs e relatórios falsos) para montar o painel `T3.0`
- [ ] Calcular as **métricas de saúde** (volume, erros, tempo de resposta…) `T3.2`
- [ ] Rascunhar no README a **base legal (LGPD)** e por quanto tempo guardamos os dados `T4.2`

---

## ⚙️ Semana 2 · 20/10 → 26/10 · Construir o principal

**Ao final da semana:** dados ruins sendo barrados, modelo treinado, dados com drift
gerados, alertas funcionando.

### 🟦 A: Dados
- [ ] Criar as **regras de qualidade** (mínimo 3, ex.: idade ≥ 18, renda preenchida, sem repetidos) `T1.4`
- [ ] ⚠️ **até seg 26/10**: Fazer as regras **bloquearem** dados ruins e gerar um relatório do erro `T1.5`

### 🟩 B: Modelo
- [ ] ⚠️ **até seg 26/10**: Treinar o modelo (XGBoost) usando só os dados de Referência `T1.8`
- [ ] ⚠️ **até seg 26/10**: Medir a qualidade do modelo e listar as colunas mais importantes `T1.9`

### 🟨 C: Drift
- [ ] ⚠️ **até seg 26/10**: Gerar os **meses simulados** (t1 a t5), com a economia piorando aos poucos `T2.3`
- [ ] Escrever os testes da sua parte `T2.7`

### 🟥 D: Painel
- [ ] Criar os **alertas** (ex.: "muitas colunas mudaram", "modelo piorou") `T3.3`
- [ ] Montar o **painel**: uma página com as métricas de saúde, os alertas e links para os relatórios `T3.4`

> 💡 D continua usando os arquivos de exemplo. Os dados reais só chegam na semana 3.

---

## 🔗 Semana 3 · 27/10 → 02/11 · Juntar as partes

**Ao final da semana:** previsões reais registradas, relatórios de drift reais, painel
usando dados reais.

### 🟦 A: Dados
- [ ] Criar um **lote de dados com erros** de propósito, para mostrar as regras barrando `T1.6`
- [ ] Escrever os testes das regras `T1.7`

### 🟩 B: Modelo
- [ ] ⚠️ **até sex 30/10**: Fazer as **previsões** dos meses simulados e registrar no log `T2.4`
- [ ] Gerar o **relatório de vieses** (o modelo é injusto com algum grupo, ex.: faixa de idade?) e escrever essa seção do README `T4.3`

### 🟨 C: Drift
- [ ] Ajustar a simulação para mexer nas **colunas mais importantes** do modelo `T2.1`
- [ ] ⚠️ **até seg 02/11**: Gerar os **relatórios de drift** no Evidently, com os testes PSI e KS `T2.6`

### 🟥 D: Painel
- [ ] Fazer o painel ler os **arquivos reais** `T3.5`

---

## 🧪 Semana 4 · 03/11 → 09/11 · Testar tudo junto e escrever o README

**Ao final da semana (seg 09/11):** 🔒 **código congelado**. Tudo roda do começo ao fim e
o README está completo. Depois disso, só correções.

### 👥 Todos
- [ ] 📞 **Quarta 04/11: encontro de integração (~1h30).** Todos rodam o projeto inteiro
  juntos. O que der erro, o dono da parte corrige.

### 🟦 A: Dados
- [ ] README: como tratamos os **dados pessoais** `T4.1`

### 🟩 B: Modelo
- [ ] Escrever o **roteiro do vídeo** (quem fala o quê, o que mostrar) `T4.6`
- [ ] Rodar os testes automaticamente a cada PR (GitHub Actions) `T0.6`

### 🟨 C: Drift
- [ ] README: **por que o modelo piorou** (causa → efeito → o que fazer) `T4.4`

### 🟥 D: Painel
- [ ] README: quais **métricas de saúde** acompanhamos `T3.6`
- [ ] README: **como rodar o projeto** e onde ver cada resultado `T4.5`
- [ ] ⚠️ **até seg 09/11**: Rodar tudo uma última vez e colocar no git os **relatórios e logs finais** (o avaliador precisa ver os logs) `T3.8`

---

## 🎬 Semana 5 · 10/11 → 17/11 · Vídeo e entrega

### 👥 Todos
- [ ] **ter 10 → sex 13/11: gravar o vídeo** (máx. 5 min). Cada um grava ~1 min da sua parte e B edita. `T4.7`
  - 🟩 B: o problema (modelos de crédito piorando sem ninguém perceber)
  - 🟦 A: o que precisávamos resolver + regras barrando dados ruins
  - 🟨 C: simulação do drift e relatórios
  - 🟥 D: painel, alertas e LGPD
- [ ] **sáb 14 → seg 16/11: revisão final**: conferir requisitos, README e link do vídeo `T4.8`
- [ ] **ter 17/11: 🎯 ENTREGA**

---

## 🎁 Extras (para quem terminar antes)

- [ ] Painel no Grafana + Prometheus (opcional no enunciado) `T3.7`
- [ ] Ajudar a escrever testes de outra parte (combine com o dono)

## ✔️ Já feito

- [x] Ambiente Python configurado (cada um só roda `uv sync`) `T0.1`
- [x] Estrutura de pastas e arquivos do projeto
- [x] Configuração do Claude e do Copilot

---

## 📖 Glossário rápido

| Termo | O que é |
|---|---|
| **Referência** | Dados "do passado", usados para treinar o modelo |
| **Produção** | Dados "do presente", onde a economia mudou |
| **Drift** | Quando os dados de hoje ficam diferentes dos dados do treino |
| **Data drift** | Mudou o perfil dos clientes (ex.: a renda subiu com a inflação) |
| **Concept drift** | Mesmo perfil, mas o comportamento mudou (ex.: agora atrasa mais) |
| **PSI / KS** | Testes estatísticos que medem o tamanho da mudança (calculados pelo Evidently) |
| **Contrato de dados** | Regras que os dados precisam seguir para entrar no modelo |
| **Dados de mentira** | Dados falsos no mesmo formato dos reais, para testar sem esperar ninguém |
| **Evidently** | Ferramenta que gera os relatórios de drift |
| **PR** | Pull Request: pedido para juntar o seu código ao projeto principal |
| **Code freeze** | Data a partir da qual não entra código novo, só correções |
