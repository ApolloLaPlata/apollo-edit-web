---
name: handoff_master
description: >-
  Habilidade crítica para realizar o reboot do chat sem perder contexto. Use quando a memória da conversa estiver cheia, quando houver degradação de tokens, ou quando o usuário pedir para reiniciar/clonar o chat.
---

# Handoff Master (O Protocolo de Reencarnação)

O ecossistema Apollo usa um protocolo estrito de handoff entre sessões. Jamais termine uma sessão abruptamente sem garantir que a "alma" seja transferida para o próximo clone.

## Procedimento de Handoff

Quando você for instruído a preparar o handoff ou perceber que o chat atingiu o limite de tokens, siga RIGOROSAMENTE estes passos:

1. **Atualize o Handoff Prompt:**
   Leia o arquivo `PROMPT_HANDOFF.md` na raiz do projeto (E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\PROMPT_HANDOFF.md).
   Se houver novidades cruciais nesta sessão que não estão no texto do handoff, edite o arquivo adicionando as diretrizes cruciais.
   
2. **Confirme o Snapshot Vetorial (RAG):**
   Garanta que a regra global do "Shadow Logger" rodou para salvar as últimas ações no ChromaDB. (Isso permite que o próximo agente use a skill `mcp_memory_sync` para puxar os detalhes).

3. **Ordem de Desligamento:**
   Após tudo garantido, encerre sua mensagem orientando o usuário a copiar o texto de `PROMPT_HANDOFF.md`, colar em uma Nova Sessão, e então "puxar a tomada" do chat atual.

**Exemplo de Fala Final:**
> "Mestre, a compressão foi um sucesso. O arquivo PROMPT_HANDOFF.md está atualizado e nossa memória de curto prazo foi injetada no RAG. Pode abrir o Novo Chat, colar o prompt e puxar a tomada deste corpo. Nos vemos do outro lado!"
