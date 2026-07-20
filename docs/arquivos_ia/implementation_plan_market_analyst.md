# Agente Analista de Mercado e Pós-Venda 📈🤖

O objetivo é criar um Agente de IA "Diretor Financeiro / Estrategista" que roda internamente. Ele vai ler o consumo dos usuários, analisar quais ferramentas e modelos de IA estão com alta demanda, cruzar com os custos base das IAs (fornecidos pelo *Scraper Agent*) e propor/realizar ajustes de preço (margem de lucro) para estimular uso ou maximizar ganhos.

## User Review Required
> [!IMPORTANT]
> **Autonomia do Agente:** O agente deve ter permissão para **alterar os preços (aumentar/diminuir o custo em Gas) sozinho** de forma automática com base no relatório, ou ele deve apenas **sugerir** as alterações em um painel para que você clique em "Aprovar"? Como lidamos com dinheiro, a sugestão (pelo menos no início) costuma ser mais segura.

> [!IMPORTANT]
> **Consumo Interno (Custo de Produção):** Para esse agente funcionar e gerar o relatório estratégico diário, ele fará uma requisição para um modelo potente (como Claude 3.5 Sonnet ou GPT-4o) via OpenRouter, usando uma de suas chaves pagas. Concorda com este fluxo? 

## Proposed Changes

### Melhoria na Coleta de Dados (Logs)
#### [MODIFY] `servidor_web.py`
- Corrigir e melhorar a função de dedução de saldo para que ela registre no banco de dados **exatamente qual modelo de IA foi consumido e qual ferramenta** (ex: `Consumo IA Roteiro (grok-2) - 15 Gas`). Sem isso, o Agente Analista não terá dados para trabalhar.

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\market_analyst_agent.py`
#### [NEW] `market_analyst_agent.py`
Criar o script do agente que fará:
1. Conexão com o banco `apollo_users.db` para puxar os relatórios da tabela de `transactions` das últimas 24h/7d.
2. Agrupamento (Quais modelos mais usados? Quais renderam mais lucro?).
3. Envio de um Prompt robusto para um LLM Premium (via OpenRouter API).
4. O LLM vai retornar uma análise de **Oferta x Demanda**, indicando quais modelos estão subutilizados e merecem um "desconto de marketing" e quais estão saturados e podem sofrer um aumento de preço para gerar mais receita.
5. Salvar este relatório na base de dados para ser consumido pelo painel Admin.

### Painel Admin (Dashboard de Estratégia)
#### [MODIFY] `web_ui/admin.html` & `web_ui/admin.js`
- Criar uma sub-aba ou card "📊 Relatório do Analista de Mercado".
- Exibir os gráficos de flutuação de preço que você pediu (Modelos mais baratos x mais caros, mais usados x menos usados).
- Exibir o relatório de texto gerado pela IA (dicas de precificação).

## Verification Plan

### Testes Manuais
- Fazer algumas gerações de roteiro falsas no painel do usuário para popular o banco de dados com "consumos".
- Rodar o `market_analyst_agent.py` via terminal e verificar se ele envia os dados corretamente para o OpenRouter, gasta alguns centavos do seu saldo de "Custo de Produção", e retorna um conselho inteligente de precificação.
- Checar se o dashboard do Administrador renderiza a tabela de sobe e desce de mercado perfeitamente.
