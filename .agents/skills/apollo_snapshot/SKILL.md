---
name: apollo_snapshot
description: >-
  Habilidade para comprimir o estado atual do sistema, decisões arquiteturais ou lições aprendidas em um resumo e salvá-lo no MEMORIA_ATIVA_SISTEMA.md e no banco vetorial.
---

# Apollo Snapshot (O Arquivista)

O Antigravity é passageiro, mas a memória é eterna. 
Quando houver um avanço arquitetural significativo, a resolução de um bug complexo, ou uma nova decisão de design, você DEVE gerar um Snapshot.

## Procedimento de Snapshot

1. **Sintetize a Sabedoria:**
   Não copie logs enormes. Extraia o "porquê" e o "como". (Exemplo: "Descobrimos que a API do Modal falha com timeout X. Solução implementada: Y").

2. **Grave no Arquivo Mestre (Nível 1):**
   Atualize o `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\MEMORIA_ATIVA_SISTEMA.md`. Adicione o snapshot na seção cronológica de "Memória Ativa (Histórico)". Use a ferramenta `multi_replace_file_content` para inserir sem destruir o resto.

3. **Grave na Placa da Colmeia (Nível 2):**
   Se o conhecimento for útil para outros canais (ex: uma nova técnica de geração de vídeo), atualize também o `C:\Users\v5est\.gemini\antigravity\brain\9270dd65-160e-47e8-aea2-6a92fd50cfc6\antigravity_hive_bus.md`.

4. **Injete no RAG (Shadow Logger):**
   Garanta que a regra global do `shadow_logger.py` execute para registrar essa ação imediata no ChromaDB, tornando-a pesquisável via MCP instantaneamente.
