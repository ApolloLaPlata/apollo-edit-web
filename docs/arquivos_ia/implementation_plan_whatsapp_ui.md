# Espelhamento de Identidade do Canal e Remoção de Comandos

## Esclarecimento Crucial sobre o "Comando Secreto"
O comando `!apollo` **nunca foi feito para os seus usuários finais**. Ele só foi necessário porque você escaneou o QR Code com o seu **próprio número pessoal** e enviou uma mensagem do seu celular para um grupo onde você mesmo está.
Quando um cliente/inscrito mandar "oi" para o número do robô, o sistema já entende que é uma mensagem externa e **responde na mesma hora, sem nenhum comando secreto**.
Mas, como você pediu, **eu vou remover o comando secreto do código**.

> [!WARNING]
> **Risco de Spam Pessoal**
> Se você mantiver o seu celular pessoal conectado no QR Code após essa remoção, o robô passará a responder **absolutamente todas as mensagens** que você receber (da sua mãe, do seu chefe, dos grupos da família), porque não haverá mais o filtro de segurança! O sistema assumirá que o WhatsApp conectado é um número exclusivo de atendimento.

## Proposed Changes

### Identidade Dinâmica no Painel (Reflexo do Canal)
Atualmente, o painel exibe "Apollo Prime" fixo. Vamos tornar o chat Camaleão:

#### [MODIFY] [apollo_agents.js](file:///E:/MEUS%20PROGRAMAS/APOLLO_EDIT_WEB/web_ui/apollo_agents.js)
- Adicionarei uma rotina de inicialização que consulta o backend para saber em qual Workspace estamos (ex: "DESCARGA NEWS").
- O nome da aba de chat, o ícone e a mensagem de saudação inicial mudarão dinamicamente para o nome do Canal atual. Ex: "Assistente DESCARGA NEWS - Online".

#### [MODIFY] [servidor_web.py](file:///E:/MEUS%20PROGRAMAS/APOLLO_EDIT_WEB/servidor_web.py)
- Vou garantir que o `chat_send` (quando você digita pelo painel Web) utilize o System Prompt específico configurado no `config.json` daquele canal, em vez de forçar o prompt do Apollo Prime. Assim, o robô responderá com a personalidade daquele canal específico!

#### [MODIFY] [index.js (WhatsApp Bot)](file:///E:/MEUS%20PROGRAMAS/APOLLO_EDIT_WEB/whatsapp_bot/index.js)
- Remoção total dos comandos `!apollo`.
- Remoção do bloqueio de grupos. O robô responderá tudo o que chegar, assumindo que a conta logada no QR Code é uma conta comercial/dedicada.

## User Review Required
> [!IMPORTANT]
> Você concorda com a remoção total dos filtros de segurança no Node.js, ciente de que o WhatsApp escaneado vai responder a tudo e todos automaticamente?
> 
> Diga **Aprovado** para eu executar essa mutação de identidade no painel e no robô.
