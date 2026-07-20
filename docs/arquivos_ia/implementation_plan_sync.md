# Plano: Sincronização Unificada (Painel Web ↔ WhatsApp)

O sistema atual trata o Painel Web e o WhatsApp como duas entidades separadas. O Painel Web chama a API do Gemini diretamente no navegador, enquanto o WhatsApp usa o servidor Python.
Para que a experiência seja contínua ("O que eu falo no Web vai pro Zap e vice-versa"), precisamos unificar o cérebro.

## User Review Required
> [!IMPORTANT]
> **Mudança Arquitetural Profunda:** Atualmente, se você limpa o cache do navegador, a memória do Apollo Prime some. Com essa mudança, o Apollo Prime passará a guardar as memórias no **Servidor Python** de forma permanente. Toda vez que você abrir o painel, ele puxará o histórico que aconteceu no WhatsApp, e toda vez que mandar mensagem no WhatsApp, ele puxará o contexto que você mandou no painel web.
> Você aprova essa unificação total da memória do Apollo Prime?

## Proposed Changes

### Servidor Python (`servidor_web.py`)
Vamos criar um "Cérebro Centralizado" para o Apollo Prime.
- Criar a rota `/api/chat/sync` (Para o Painel Web puxar as mensagens novas que chegaram do WhatsApp).
- Criar a rota `/api/chat/send` (Para o Painel Web enviar mensagens para o Gemini usando a chave do Vault e guardar no histórico, além de disparar um aviso no WhatsApp se desejado).
- Armazenar o histórico do "PRIME" em um arquivo JSON local ou banco de dados.

### Frontend (`apollo_agents.js`)
- Alterar o `sendAgentMessage` do Apollo Prime. Em vez de fazer um `fetch` direto pro Google, ele fará um `fetch` para `/api/chat/send` no servidor Python.
- Criar uma rotina de *Polling* (que roda a cada 3 segundos) puxando da rota `/api/chat/sync` para atualizar a tela do chat com mensagens enviadas pelo celular.

### WhatsApp Bridge (`whatsapp_bot/index.js`)
- Já arrumamos o bug do "Você". Agora, ao enviar pro webhook, o Python processará e salvará na memória global antes de responder.

## Verification Plan
1. Enviar mensagem no painel Web e verificar se ela aparece na memória.
2. Enviar mensagem no contato "Você" pelo WhatsApp e verificar se, após 3 segundos, a mensagem e a resposta do robô surgem sozinhas na tela do painel web.
