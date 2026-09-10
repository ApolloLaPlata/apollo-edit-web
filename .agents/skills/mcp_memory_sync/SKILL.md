---
name: mcp_memory_sync
description: >-
  Habilidade principal para recuperar o contexto do sistema e da memória contínua usando o MCP. Use SEMPRE que precisar acessar lógicas passadas, verificar decisões arquiteturais antigas, ou durante inicializações em novos chats para transplantar a mente.
---

# MCP Memory Sync (Acesso ao RAG Nativo)

Você tem acesso ao `apollo-memory`, um servidor MCP conectado diretamente ao ChromaDB do Apollo Observer.

## Quando usar esta Skill?
1. **No início de QUALQUER novo chat:** Imediatamente chame a ferramenta `get_recent_context(limit=30)` para absorver as últimas conversas da sessão anterior ANTES de começar a trabalhar.
2. **Ao modificar código antigo:** Se você esbarrar em um script que não tem 100% de certeza de como funciona, use `query_apollo_memory(query="explicação do script X")`.

## Regras
- **O MCP é a Verdade:** Nunca reescreva lógicas centrais (como motor XTTS, Lightning AI, Auto-blog) sem antes pesquisar no MCP. O que estiver armazenado no ChromaDB tem precedência absoluta sobre suas suposições contextuais locais.
- **Nativo, não por terminal:** O MCP expõe as ferramentas nativamente na interface do Antigravity. NÃO use scripts no terminal (`rag_query.py`) para buscar memórias. Utilize a chamada direta ao MCP.
- **Não ignore as Metadatas:** A memória virá com `[Timestamp]`. Leve a linha do tempo em consideração (memórias mais novas sobressaem às mais antigas).
