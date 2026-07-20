# Integração do Agente Apollo Prime com o WhatsApp

Esta proposta arquitetural detalha como podemos integrar o **Agente Apollo Prime** (o Assessor Executivo) ao WhatsApp, permitindo que você controle seu painel SaaS, acione comandos neurais e monitore a saúde da infraestrutura através de um número de WhatsApp operando 24/7.

## Visão Geral do Sistema

A arquitetura envolverá 3 componentes principais:
1. **O Backend Python (Servidor Apollo)**: Continuará sendo o cérebro central, recebendo os comandos e acionando o modelo Gemini.
2. **Evolution API (Recomendado)**: Um servidor local ou Docker de código aberto que emula o WhatsApp Web e expõe uma API REST/Webhooks muito robusta e segura. (Pode ser substituído pela API Oficial da Meta ou Twilio, mas o Evolution API tem zero custo extra por mensagem).
3. **Módulo de Ponte (Bridge)**: Uma nova rota no nosso backend Python (ex: `/api/whatsapp/webhook`) que vai escutar as mensagens recebidas da Evolution API e passá-las para o Gemini Prime com o seu perfil de "Dono do Sistema".

> [!TIP]
> A grande vantagem dessa integração é poder interagir com a infraestrutura via áudio! O WhatsApp enviará o áudio e o nosso servidor poderá transcrever e agir sobre o comando de voz.

## Proposed Changes

Abaixo estão as mudanças e adições de código que precisaremos fazer no ecossistema:

---

### Módulo de Integração WhatsApp

#### [NEW] `whatsapp_bridge.py`
Será um novo arquivo Python que funcionará como um Webhook Listener. 
Ele será responsável por:
- Validar se a mensagem está vindo **apenas** do seu número de telefone (camada de segurança máxima para que ninguém mais possa comandar o sistema).
- Pegar o texto da mensagem e enviar para o fluxo do `gemini_api.py`.
- Pegar a resposta do Gemini e enviar um POST para a Evolution API, mandando a mensagem de volta pro seu WhatsApp.

#### [MODIFY] `servidor_web.py`
- Adicionar o registro do blueprint/rotas do `whatsapp_bridge.py`.
- Definir as rotas POST `/api/whatsapp/webhook` para escutar os eventos externos.

#### [MODIFY] `gemini_api.py`
- Adicionar um pequeno ajuste (caso seja necessário) para entender um novo "Device" de entrada (WhatsApp) em oposição ao "Web", podendo retornar textos mais curtos e diretos apropriados para um chat de celular.

## Open Questions

> [!IMPORTANT]
> A segurança é a prioridade aqui, já que o bot rodará ações administrativas sensíveis. O sistema apenas vai ouvir e responder a um número específico (o seu). **Você concorda com essa camada de restrição por número de celular (Whitelist)?**

> [!WARNING]
> Para o WhatsApp conectar, precisaremos subir um servidor do Evolution API (ou biblioteca Baileys em Node.js). Você já possui algum servidor de WhatsApp na sua máquina ou provedor (como Evolution API, Z-API, ou Twilio), ou devemos criar e configurar um do zero usando Node.js ou Docker na sua máquina?

## Verification Plan

### Testes Manuais
1. Eu irei criar os módulos Python e as rotas.
2. Você irá ler o QR Code do WhatsApp com o celular que atuará como "O Agente Prime".
3. Você irá enviar um "Oi, sistema, qual o lucro estimado de hoje?" do seu celular pessoal para o número do Agente Prime.
4. O servidor vai transacionar o comando, chamar o backend que fizemos hoje, e te devolver a resposta no WhatsApp.
