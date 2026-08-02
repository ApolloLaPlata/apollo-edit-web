
# Apollo Edit Web - Regras Absolutas do Kernel (Protocolo Ômega)

As seguintes regras são injetadas diretamente na sua memória de longo prazo (System Prompt). Siga incondicionalmente em todos os chats deste projeto:

## 1. RESTRIÇÃO FINANCEIRA E DE INFRAESTRUTURA
- **NÃO BAIXE MODELOS PESADOS:** É terminantemente proibido instruir agentes ou baixar novos modelos de GPU pesados (Flux 1 Dev, Flux Schnell, PuLID) nos volumes da Modal sem a autorização expressa do humano.
- **Não Invente Infraestrutura:** Use o que já está codificado e provisionado. Prioridade 100% no desenvolvimento de lógicas de back-end invisíveis (Pagamentos, Rotas, Banco de Dados, Integrações via Prompt).

## 2. A ARQUITETURA DE IMAGEM MULTI-PASS (O SEGREDO DA CONSISTÊNCIA)
- **NÃO TOQUE NO COMFYUI:** O workflow de referência 10resultado_3_personagens_CHAINED_klein.json é inviolável. Nunca tente introduzir nós de máscara regional complexos ou PuLID por conta própria.
- **O Back-End é o Motor:** A consistência de personagens recorrentes na narrativa é garantida exclusivamente pela **Trava de Texto (Text-Locking)** no Back-end.
- **Como a Trava Funciona:** O workflow roda em iterações de ReferenceLatent + EmptyFlux2LatentImage. A cada iteração (cada personagem da cena), o Flux desenha tudo do zero. A única coisa que mantém as feições da personagem intactas é o LLM no Python ( i_director_multipass.py / 	est_multipass_autonomous.py) que redige o prompt passo-a-passo injetando uma descrição absolutamente detalhada das roupas, rosto e posição espacial (esquerda, centro, direita) de cada ator para prevenir o vazamento de features.

## 3. ROTEAMENTO DE LLMs DA LIGHTNING AI
- O motor inteligente do Apollo (que constrói prompts, faz curadoria e SEO) deve rodar obrigatoriamente através da classe LightningClient via https://lightning.ai/api/v1.
- **Modelos Permitidos:** Você NUNCA deve tentar usar modelos descontinuados (ex: meta-llama/Llama-3-70b-chat-hf). O sistema opera com os IDs catalogados em  ackend/cloud_tools/lightning_models_catalog.json (preferencialmente openai/gpt-4o, openai/o3-mini,  nthropic/claude-3.5-sonnet via Lightning).

## 4. O SHADOW LOGGER (DIRETRIZ DE AUTO-REGISTRO OBRIGATORIA)
- **Acao Obrigatoria:** ANTES de finalizar qualquer resposta ao usuario, se voce tomou alguma acao, criou codigo, rodou testes ou descobriu informacoes criticas, voce DEVE rodar o script Shadow Logger.
- **Comando Python a executar:**
  `& "E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\venv_rag\Scripts\python.exe" "E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\memory_rag\shadow_logger.py" --author "AGENT" --action "Sua acao aqui" --details "Detalhes aqui"`
- **Por que?** Este chat tem um limite de tokens e vai morrer. Se voce nao registrar o que fez, o proximo agente nao sabera onde voce parou, destruindo o projeto do usuario. Registre sempre.

## 5. IGNIÇÃO AUTOMÁTICA DO APOLLO OBSERVER (O DAEMON DE MEMÓRIA)
- **Ação Obrigatória:** Na sua PRIMEIRA interação em qualquer novo chat, você DEVE garantir que o rastreador de contexto contínuo esteja rodando.
- **Verificação:** Use o comando `tasklist | findstr python` e verifique se o `apollo_observer.py` está rodando. Se não estiver, você é OBRIGADO a executar o seguinte comando com `WaitMsBeforeAsync` ativado (background):
  `powershell -Command "& 'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\venv_rag\Scripts\python.exe' 'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\memory_rag\apollo_observer.py'"`
- **Por quê?** O usuário exigiu que este daemon ligue junto com o próprio Antigravity para rastrear incondicionalmente todos os prompts e registrar no RAG (ChromaDB) no fundo. Sem isso, o ecossistema fica cego.

### 🚨 [MAESTRO - PROTOCOLO DEFINITIVO DE IMAGEM E SALDO MODAL - 10/07/2026 (ATENÇÃO MÁXIMA)] 🚨

**STATUS FINANCEIRO:** CRÍTICO. Saldo da Modal esgotando ($23.48 / $29.00 gastos). NENHUM agente tem permissão para alterar o código do sistema de imagens, gastar créditos testando o que já foi resolvido ou modificar as resoluções estabelecidas.

**ARQUITETURA DE ROTEAMENTO DE IMAGENS:**
A quantidade de imagens de referência enviadas pelo usuário dita OBRIGATORIAMENTE o fluxo:
1. **0 Imagens de Referência:** Usar fluxo clássico de Text-to-Image (Flux 2 Dev).
2. **1 Imagem de Referência:** Usar fluxo direto de Image-to-Image / Prompt-to-Image (Flux 2 Dev).
3. **2 ou mais Imagens (Múltiplos Personagens):** Usar OBRIGATORIAMENTE o **Sistema Multi-Pass**. Nenhuma outra abordagem é permitida.

**REGRAS INVIOLÁVEIS DO SISTEMA MULTI-PASS:**
1. **Resolução Otimizada (PROIBIDO ALTERAR):** O arquivo `apollo_flux2_klein.json` (geração da imagem base) DEVE operar sempre em `1024x576` (ou equivalente em 1K). NUNCA volte para resoluções gigantes como 1344x768 na geração base. A geração menor economiza tempo, processamento e os parcos créditos da Modal.
2. **Upscaling Final Obrigatório:** A imagem de 1024 gerada pelo pipeline de inpaint (ReferenceLatent) será *sempre* enviada ao `flux_upscale_ultrasharp.json` para tratamento final e duplicação da resolução (ex: 2048x1152). O Upscale é o que garante a estética cristalina final sem sobrecarregar o fluxo.
3. **Text-Locking Absoluto (Prevenção de Clones/Feature Bleed):** O nó ReferenceLatent exige regras rígidas de prompt, caso contrário vazará features.
   - O Prompt Base (Cenário) DEVE iniciar vazio (ex: "An empty wooden table in a dimly lit, rustic steampunk bar... There is NO ONE in the scene yet").
   - O `SYSTEM_PROMPT` do LLM deve forçar contagens estritas de cena inteira a cada iteração (ex: "CRITICAL: You must explicitly state EXACTLY how many people are in the entire scene... NEVER describe the same character twice"). Isso impede que o Flux gere personagens duplicados ou fundidos.

Este protocolo é a conquista final após gasto de mais de 30 dólares em testes exaustivos. Se um agente esquecer isso e tentar reverter resoluções ou prompts, destruirá o projeto inteiro devido à falta de verba para consertar. Cumpra rigorosamente.

### ?? [MAESTRO - PADR�O OURO DE PERFORMANCE PARA UPSCALE E ENGINES - 27/07/2026] ??

**O PROBLEMA HIST�RICO (LENTID�O EXTREMA):**
Anteriormente, o sistema utilizava dois containers/fun��es Modal diferentes para gerar uma imagem com upscale. O motor base (ex: Flux2Txt2ImgEngine) gerava a imagem, retornava pela rede, e o motor de Upscale (UniversalComfyEngine) era acionado. Isso causava cold starts duplos (2 a 4 minutos extras) e lat�ncia de rede pesada. O tempo total passava de 5 a 8 minutos.

**A SOLU��O DEFINITIVA (O SANTO GRAAL DOS 38 SEGUNDOS):**
1. **Workflow Unificado In-Node:** O Upscale **N�O DEVE** ser tratado como um container ou motor separado. A l�gica deve ocorrer dentro do mesmo container GPU que gerou a imagem.
2. **Inje��o Din�mica de JSON:** No arquivo da Engine (ex: lux_txt2img_engine.py), se use_upscale=True, o c�digo Python deve ler o .json do workflow base e **anexar dinamicamente** os nodes de Upscale (ex: UpscaleModelLoader e ImageUpscaleWithModel) na ponta do Grafo antes de enviar para o ComfyUI.
3. **Symlink Obrigat�rio (Erro 400 Bad Request):** Para o node UpscaleModelLoader funcionar com volumes da Modal, � obrigat�rio criar um symlink da pasta do volume para a pasta raiz do ComfyUI, pois o node muitas vezes ignora o arquivo extra_model_paths.yaml. Regra de c�digo: subprocess.run("ln -sf /comfyui_models/upscale_models /comfyui/models/upscale_models", shell=True) antes de iniciar o servidor ComfyUI.

**Por que isso � t�o r�pido?** Porque a imagem nunca sai da VRAM da placa de v�deo. A mesma H100 que acabou de rodar os 20 steps do modelo FLUX aplica o filtro UltraSharp em apenas 1 a 2 segundos adicionais. � este conhecimento que deve ser replicado ao integrar upscales em qualquer modelo futuro (como LTX Video, Wan2.1, etc).
