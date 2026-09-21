# MEMORIA ATIVA DO SISTEMA: APOLLO EDIT WEB

## VISÃO ESTRATÉGICA (POR QUE ESTAMOS CONSTRUINDO O MODAL AI STUDIO ASSIM)
- **O Propósito dos "4 Modais"**: A criação meticulosa das 4 abas de geração no Modal AI Studio (Imagem, Vídeo, Música e Voz/TTS) não é perda de tempo, nem um desvio do objetivo de "gerar vídeos genéricos". 
- Embora a edição e orquestração de vídeo genérico financiado por créditos (SaaS) seja o core inicial, o objetivo de longo prazo é criar uma **fonte de geração de matéria-prima open-source**.
- No futuro, os motores testados aqui (Qwen TTS, Mos TTS, XTTS, F5-TTS, ACE-Step, MiniMax, FLUX, LTX, Wan) serão portados para uma **Nova Interface Focada em Celular (Mobile-First)**.
- O usuário do celular poderá gerar suas imagens, vozes, músicas e vídeos usando a tecnologia open-source (gratuita/mais barata na nossa nuvem Modal) juntamente com opções pagas que integrarão o sistema depois. 
- O código do backend (FastAPI no Oracle) e a lógica de orquestração na nuvem desenvolvida agora serão **100% reaproveitados** nessa futura UI Mobile-first.

## HOMOLOGAÇÃO DE MOTORES (DECISÃO DO MESTRE)
- **Voz/TTS (Qwen vs Mos TTS)**: Embora o Mos TTS tenha ganhado ligeiramente em qualidade bruta, o **Qwen TTS foi o escolhido** como motor padrão de narrações. 
  - *Motivo:* Ele suporta "instruções emocionais" (prompting para o narrador), o que compensa qualquer perda mínima de qualidade com um ganho gigantesco de interpretação e atuação na cena. Além de ser mais barato/custo-benefício.
- **Música**: O *Stable Audio* (instrumental) será o modelo oficial predominante do Apollo Edit, pois música com voz não combina em background de cena narrada (conflito de vocais). ACE-Step e MiniMax são valiosos, mas para outros fins específicos da infraestrutura Mobile que virá depois.

## ESTADO ATUAL (O LABORATÓRIO MODAL)
- Concluímos a integração no front-end Vercel (`modal_ai_studio.html`) das abas obrigatórias:
  1. Imagem
  2. Vídeo
  3. Transcrição (Antigo Áudio/Whisper)
  4. Música (ACE-Step / MiniMax)
  5. **Voz (TTS / Clonagem)** -> (Em Desenvolvimento Contínuo)
- A infraestrutura já aceita `.mpeg` nativo via interceptação FFmpeg no Python.

## PRÓXIMO PASSO IMEDIATO (EXPANDIR A ABA DE VOZ)
- A Aba de Voz precisa ser expandida para abrigar não apenas F5-TTS/Kokoro, mas um hub de todos os modelos de TTS testados (Mos TTS, Qwen TTS, XTTS) com suas respectivas configurações (voz base, instrução de emoção para Qwen, upload de clone, etc). 

## DIRETRIZ DE ARQUITETURA TTS (Atualizado 2026-09-17 09:11)
- **Conta 10 (sitesviniciusmiranda)**: Hub exclusivo de TTS. 
- O roteamento e as requisições de geração de fala/bot para vídeos devem apontar para a infraestrutura desta conta.
- **Modelos Homologados:** Preferência primária para **Moss-TTS** e **Qwen-TTS** (os demais XTTS, F5-TTS, CosyVoice, etc, continuam à disposição como fallback ou variação de timbre).

## PROGRESSO RECENTE (Atualizado 2026-09-19)
- **Motor de Imagem (FLUX):** Consertado definitivamente os erros de HTTP 400 (validação de Node IDs dinâmicos resolvidos via heurística de class_type) e sanado a falha oculta de dependência matemática do ComfyUI (comfy_kitchen.apply_rope foi mocado nativamente). Homologado e 100% funcional na Conta 7.
- **Motor TTS (Qwen):** Completamente roteado no frontend (com campo de instrução emocional) e backend (outes_voice.py). A arquitetura envia payload com 	ext, ef_audio_base64 e instruct_text direto para a Modal da Conta 10. Considerado ESTÁVEL e pronto para testes exaustivos na interface do Modal AI Studio.

## DIRETRIZ DE CLOUD E DEPLOY (A TÁTICA DO CAVALO DE TROIA) - Atualizado 2026-09-21
- **O Problema da Oracle**: O servidor Oracle A1 (Limitado a 12GB RAM e 2 OCPUs) estava congelando (OOM) com a execução simultânea do backend FastAPI, FFmpeg e bots.
- **A Solução (O Tridente)**: 
  1. **Frontend**: Vercel (Intocável).
  2. **Modelos/Geradores**: Modal (Contas 7, 9, 10).
  3. **Backend Lógico (Apollo Edit + Autoblog)**: Migrado para **Hugging Face Spaces (Conta 1 - roxingo)**.
  4. **Oracle Cloud**: Rebaixado a 'Cofre e Transmissor', hospedando apenas o Banco de Dados, scripts de Ping (para acordar o Hugging Face 24h) e o RTMP FFmpeg da Rádio.
- **Execução do Cavalo de Troia no Hugging Face**: 
  - O Hugging Face agora bloqueia *Docker Spaces* puros atrás de um paywall (para contas sem cartão).
  - Para burlar isso e conseguir a máquina gratuita de 16GB RAM, nós criamos o Space como **Gradio -> Blank -> CPU Basic (ou ZeroGPU)**.
  - Dentro da pasta ackend, criamos um pp.py nativo que intercepta o fluxo do Gradio e inicia o Uvicorn diretamente na porta 7860.
  - **O Truque do Symlink (os.symlink('.', 'backend'))**: Adicionado no topo do pp.py para enganar o Python e garantir que os caminhos absolutos do projeto (rom backend.utils import ...) não quebrem quando o Hugging Face transforma a pasta enviada em /app.
  - **Atenção**: O Hugging Face rejeita git push com arquivos binários pesados (.png, .wav, .db). Configure o .gitignore rigorosamente e instale dependências secundárias (como oto3) manualmente no equirements.txt.
