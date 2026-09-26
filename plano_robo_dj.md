# Implementação do Robô DJ e Integração da Arquitetura

O Cérebro da Rádio (Backend no HF 1) precisa de inteligência ativa. Atualmente, ele tem rotas passivas (/next-action e /enqueue). Precisamos construir o Maestro ativo que escuta, pensa, fala e coloca as falas na fila.

## Componentes a serem desenvolvidos

### 1. ackend/services/robo_dj.py (O Maestro Ativo)
Um worker em background que:
1. Geração de Texto: Chama a Lightning AI para gerar falas curtas, dinâmicas e bilíngues.
2. Geração de Áudio: Chama o QwenTTSClient (Modal) para transformar o texto em voz.
3. Hospedagem Temporária: Onde o áudio será salvo para que a Oracle possa baixar? Como o backend vive no HF, podemos salvar na pasta /tmp/ do HF e servir via FastAPI (ex: /api/static/audio.mp3), ou fazer o upload para o HD virtual do HF Conta 2. Servir pelo FastAPI é mais rápido.
4. Enfileiramento: Dá um POST no /enqueue com o JSON final contendo a URL do áudio.

### 2. ackend/services/youtube_chat_listener.py (Os Olhos)
Um script levíssimo usando a biblioteca pytchat ou API Oficial do YouTube que escuta a Live.
- Filtra mensagens de Superchat.
- Se houver Superchat, corta a fila do Robô DJ e manda a LLM agradecer nominalmente.

## A Grande Mudança (Adeus OBS Local)
O código antigo ackend/bots/radio_broadcaster.py salvava o áudio no PC local para o OBS Studio. 
Nós vamos abandonar essa prática. O novo obo_dj.py viverá na Nuvem (HF Conta 1) e enviará tudo direto para a fila em memória, e a Oracle 2 fará o download.
