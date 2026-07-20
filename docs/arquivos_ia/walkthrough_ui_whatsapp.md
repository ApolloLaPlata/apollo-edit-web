# Customização Dinâmica e Espelhamento

A arquitetura do sistema foi atualizada para comportar a visão "Canal por Canal" (Robô White Label) e o Chat Universal sem comandos secretos.

## Alterações Realizadas

### 1. Interface do Painel Adaptativa
O painel de controle Web foi redesenhado nos bastidores para atuar como um "Camaleão".
- Antes, a aba principal sempre dizia "Apollo Prime" e agia como o CEO do software.
- Agora, quando a página carrega, ela **consulta o servidor** para descobrir qual é o Canal logado (ex: "DESCARGA NEWS").
- O título, nome e texto da primeira mensagem mudam para refletir que você está conversando com a **IA oficial daquele Canal**.

### 2. Personalidade da IA (System Prompt)
- A IA do painel (quando no contexto do Canal) não usa mais a "memória do Apollo Prime".
- Ela automaticamente adota o `System Prompt` específico que você escreveu no `config.json` do seu Workspace. Se a sua IA for o "Rafael", o painel Web responderá como o Rafael!

### 3. Remoção de Filtros de Segurança no Node.js
- O robô do WhatsApp (`whatsapp_bot/index.js`) teve todas as suas "amarras" de segurança cortadas, conforme o seu pedido.
- Não existem mais comandos secretos.
- O robô irá processar **imediatamente** qualquer mensagem que entrar no WhatsApp daquele número, repassá-la ao Python e devolver a resposta na mesma hora, **sem necessidade de prefixos como !apollo**.

> [!WARNING]
> Como o filtro anti-spam foi desligado, recomendo que este sistema seja utilizado apenas em números de WhatsApp dedicados (chips novos comprados para o canal), caso contrário a IA poderá enviar respostas automáticas não desejadas aos seus contatos pessoais.
