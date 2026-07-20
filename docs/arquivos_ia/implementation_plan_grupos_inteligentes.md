# Arquitetura de Múltiplos Robôs com Chip Único (Grupos Inteligentes)

## A Física do WhatsApp (Aviso Importante)
Como o cliente vai escanear o QR Code com o **próprio celular pessoal dele**, o robô operará "de dentro" do celular do cliente. Isso significa que as respostas do robô aparecerão como **mensagens enviadas por ele mesmo** (balões verdes do lado direito).
**É impossível** no WhatsApp que o seu próprio número mande uma mensagem para você mesmo e ela chegue do lado esquerdo parecendo outra pessoa.
A mágica que faremos para contornar isso é usar **Grupos**. O Grupo será a "Sala do Robô", e a foto do Grupo será o "Avatar do Robô".

## O Fluxo de Funcionamento

### 1. Criação Automática do Grupo do Canal
No Painel de Administração de cada Canal, teremos uma função (botão ou automático) para **Vincular ao WhatsApp**.
- O Node.js vai criar um grupo vazio chamado `🤖 Assistente: [Nome do Canal]`.
- O Node.js vai aplicar a **Logo do Canal** como foto principal desse grupo.
- O Node.js devolve o `ID do Grupo` para o Python.

### 2. Memória Isolada por Canal
- O Python salvará o `ID do Grupo` dentro da pasta de configurações daquele Canal específico.
- Você (ou seu cliente) pode ter 10 canais. O sistema criará 10 grupos no WhatsApp dele, cada um com uma foto.

### 3. O Roteador Inteligente (Webhook)
Quando você abrir o WhatsApp e mandar um "Oi" lá no grupo do Canal 3:
- A mensagem chega no Node.js e vai pro Python.
- O Python vai olhar e dizer: *"Opa, essa mensagem veio do Grupo ID XYZ"*.
- Ele vasculha o sistema e descobre: *"Esse Grupo pertence ao Canal 3"*.
- O Python então carrega **exclusivamente a personalidade, os dados e o histórico do Canal 3**, gera a resposta e manda o robô responder lá dentro do grupo do Canal 3!

## Proposed Changes

### [NEW] Endpoint no Node.js (`whatsapp_bot/index.js`)
- Criar a rota POST `/api/create_channel_group` que aceita `nome` e `foto_base64`.
- Usar `client.createGroup(nome, [])` para criar um grupo apenas com você mesmo.
- Usar `client.setProfilePic` para colocar a logo do canal no grupo recém-criado.

### [MODIFY] Roteador no Python (`servidor_web.py`)
- O `whatsapp_webhook` deixará de olhar apenas para o `CURRENT_WORKSPACE_PATH`.
- Ele precisará iterar sobre as pastas de todos os Workspaces registrados no sistema (canais do usuário) e verificar qual deles possui o `whatsapp_group_id` correspondente ao grupo de onde a mensagem veio.
- Dessa forma, o motor da IA carregará o `config.json` correto daquele canal específico, operando 100% isolado dos outros.

## User Review Required
> [!IMPORTANT]
> Você está ciente de que, como o robô usará o celular do próprio cliente, as respostas dentro do grupo aparecerão do "lado direito" (balões verdes de mensagens enviadas)? O cliente não falará com "outro contato", ele falará "dentro de um grupo temático" que o sistema criou para ele.
>
> Se esta estrutura de "Grupos Inteligentes" atende à sua visão de negócio escalável (zero chips extras para o cliente), responda com **Aprovado** para eu iniciar a programação!
