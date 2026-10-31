# Guia de Governança e LGPD (base para o README)

Material de apoio para a Etapa 4. A versão final **precisa** estar consolidada no
`README.md` (exigência do enunciado). Este arquivo guia o que deve ser escrito e serve de
contexto para as IAs ao redigir essa seção.

## O que o README precisa responder (critério: 15%)

1. **Como a PII foi tratada neste projeto**
   - Inventário das colunas: quais são PII diretas (nome, CPF, endereço), quais são
     indiretas/quasi-identificadores (CEP, data de nascimento, empregador) e quais são
     sensíveis (art. 5º, II, da LGPD: origem racial, saúde etc.).
   - Ações tomadas: remoção, pseudonimização (hash com salt), generalização (faixas de
     idade/renda), minimização (só as features necessárias).
   - Logs de predição sem PII. Os IDs são pseudonimizados.
   - Dados fora do Git (`.gitignore`) e acesso restrito.
2. **Base legal para a decisão de crédito**
   - Art. 7º, X, da LGPD: **proteção do crédito**. Também cabem execução de contrato /
     procedimentos preliminares (art. 7º, V) e legítimo interesse (art. 7º, IX), conforme
     o caso.
   - Art. 20: **direito à revisão** de decisões automatizadas e a explicações sobre os
     critérios (explicabilidade, ex.: importância de features/SHAP).
   - Menção à Lei do Cadastro Positivo (Lei 12.414/2011), quando aplicável.
3. **Plano de retenção**
   - Prazo por tipo de dado (dados de treino, logs de predição, relatórios agregados),
     com justificativa (ex.: prazo de guarda de obrigações legais/regulatórias e
     finalidade de monitoramento).
   - Descarte/anonimização ao fim do prazo. Relatórios agregados (sem PII) podem ser
     mantidos.
4. **Mitigação de vieses**
   - Atributos protegidos (ou proxies) fora das features do modelo.
   - Métricas de fairness por grupo (ex.: taxa de aprovação/default por faixa etária),
     quando houver dados para isso.
   - Monitorar viés junto com o drift: o drift pode afetar mais um grupo do que outro.
5. **Privacy by Design e by Default**
   - Minimização, pseudonimização, segurança, transparência e privacidade como padrão do
     pipeline.
6. **Análise causal da degradação**
   - Ligar a causa econômica simulada (ex.: inflação → renda nominal sobe mas o poder de
     compra cai; desemprego ↑ → default ↑) aos efeitos observados: features com drift
     (PSI/KS), mudança na distribuição do score, queda de AUC/KS (concept drift).
   - Separar correlação de causalidade: o que o monitoramento mostra (associação) e o que
     sabemos por construção da simulação (causa).
   - Prescrição: ação recomendada (retreinar, recalibrar, revisar a política de corte,
     ampliar as regras do contrato) e quem decide (governança do modelo).

## Papéis de governança sugeridos

| Papel | Responsabilidade |
|---|---|
| Dono do modelo | Aprova retreino/rollback, define thresholds de alerta |
| Engenharia de ML | Mantém pipeline, contratos e monitoramento |
| Encarregado de dados (DPO) | Valida base legal, retenção e atendimento a titulares |
| Risco/Compliance | Revisa vieses e impactos da decisão automatizada |
