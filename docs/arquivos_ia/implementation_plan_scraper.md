# Agente Coletor de Preços de IA (Pricing Scraper Agent)

A necessidade aqui é criar um Agente Autônomo interno do Apollo que faça a varredura e a atualização diária dos preços de Inteligência Artificial, isentando o usuário de gerenciar as tabelas de `models_pricing` manualmente e notificando sempre que houver oportunidades mais baratas ou lançamentos de mercado.

## User Review Required
> [!IMPORTANT]
> **API do OpenRouter como Fonte de Verdade:** Em vez de fazer web scraping (que quebra toda vez que um site muda o design), recomendo usarmos a própria API oficial de modelos do OpenRouter (`https://openrouter.ai/api/v1/models`). Como o OpenRouter é um agregador, ele já mapeia quase todos os modelos existentes (incluindo Groq, DeepSeek, Llama, OpenAI, Anthropic), com preços em tempo real por token. Você concorda em centralizarmos a busca de preços puxando os dados consolidados do OpenRouter?

> [!IMPORTANT]
> **Notificações:** O agente será programado para gerar uma notificação no painel do Apollo sempre que detectar um modelo novo, para que você decida se quer ativá-lo ou ignorá-lo. Isso atende a sua necessidade de "me comunicar pra depois eu chegar e instalar os modelos novos"?

## Proposed Changes

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\pricing_scraper_agent.py` (Novo)
#### [NEW] `pricing_scraper_agent.py`
Será criado um novo script Python dedicado para esta tarefa:
1. Faz requisição à API de Modelos do OpenRouter (e/ou scrape de páginas fallback).
2. Converte os preços de "custo por token" para "custo por 1 Milhão de Tokens" (padrão Apollo).
3. Verifica se o `model_id` já existe no banco `models_pricing`. Se não existir, insere com `status = 'Inativo'` para não bagunçar a produção imediatamente.
4. Se já existir, verifica se o preço mudou. Se mudou, atualiza os valores de Input e Output.
5. Se for identificado como "0" (zero custo), classifica automaticamente na Tier `Free`.
6. Envia uma notificação/alerta (salvo no banco ou via log interno) se detectar modelos virais novos (com base em trending/relevância).

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py`
#### [MODIFY] `servidor_web.py`
- Adicionar uma tarefa assíncrona com a biblioteca `apscheduler` ou `asyncio` (Background Tasks do FastAPI) para rodar a função de atualização do `pricing_scraper_agent.py` a cada 24 horas.
- Incluir uma rota de "Sincronizar Manualmente" para você forçar a busca na área administrativa quando quiser.

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\admin.html`
#### [MODIFY] `admin.html`
- Adicionar um botão "Sincronizar Preços Agora" na aba de "Preços de Modelos".
- Uma pequena central de alertas no topo informando "X modelos novos descobertos pelo agente. Verifique a lista".

### Estratégia de Chaves OpenRouter (Pagas x Gratuitas)
Como você mencionou, você vai rodar 14 chaves Free do OpenRouter e 5 chaves Pagas. Para o sistema diferenciar, nós podemos:
1. Adicionar uma flag `key_tier` (Paga vs Gratuita) na nossa futura gestão de chaves (quando formos implementá-las).
2. O Meta-Agente vai saber: se a rota usar um modelo Free (onde o preço no painel for 0), ele roteia pelo pool de 14 chaves gratuitas. Se a rota pedir um modelo Premium (onde o preço for maior que 0), ele roteia pelo pool das 5 chaves pagas. (Isso será documentado para o módulo de Rodízio de Chaves).

## Verification Plan

### Manual Verification
- Clicar em "Sincronizar Preços Agora" no painel e observar se a tabela de modelos é preenchida com as dezenas de modelos ativos do mercado e seus preços atualizados.
- Checar se modelos lançados recentemente (como o Nemotron, Llama 3.2, etc.) aparecem como Inativos aguardando aprovação.
