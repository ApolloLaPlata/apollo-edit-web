# PLANO FASE B — ECOSSISTEMA E ORQUESTRAÇÃO
## Tutorial das Coisas | Expansão Futura (Só depois da Fase A concluída)

> **REGRA DE OURO:** Esta fase só começa quando a Fase A (Editor Inteligente) estiver 100% completa.
> O objetivo aqui é fazer os SOFTWARES SE COMUNICAREM, eliminando cópias manuais de arquivo.
> Este NÃO é o roteiro automático nem o postador automático. É a PONTE entre etapas manuais.

---

## CONTEXTO: COMO O FLUXO DO USUÁRIO FUNCIONA HOJE

```
[Agente Gemini Web] → roteiro/prompts
       ↓ (cópia manual)
[Editor Python] → gera áudio (TTS) + edita vídeo
       ↓ (cópia manual)
[AutoFlow/Meta Apollo - Extensão] → gera imagens/vídeos
       ↓ (cópia manual)
[Editor Python] → monta o vídeo final
       ↓ (cópia manual)
[Postador - Extensão] → usuário faz upload + aprova
```

O objetivo da Fase B é **eliminar as cópias manuais intermediárias**, mantendo o controle humano nos pontos de decisão.

---

## AS 20 ETAPAS DA FASE B

### BLOCO 1: PONTE EDITOR → EXTENSÕES (Sem Postagem Automática)

**[B1] — Pasta Monitorada (Hot Folder) para o Postador**
- O QUE FAZER: O editor Python, ao concluir um vídeo, salva em uma pasta monitorada (`_prontos_para_postar/`) com um `info.json` contendo título, descrição e tags (gerados pelo agente Gemini já no roteiro). O postador detecta a pasta e pré-preenche os campos automaticamente. O CLIQUE DE ENVIO é sempre manual.
- IMPACTO: Elimina copiar/colar o título e descrição. O usuário só clica "Enviar".
- NOTA: Diferente do que foi feito antes (postagem cega). Aqui o usuário SEMPRE aprova.

**[B2] — Redesign Visual do Postador (Estilo AutoMetaAPOLLO)**
- O QUE FAZER: Refazer o `popup.html` das extensões de postagem com o visual premium do AutoMetaAPOLLO (dark mode, gradientes, ícones de plataforma visuais). Manter toda a lógica existente, apenas melhorar a UI.
- REFERÊNCIA: `e:\MEUS PROGRAMAS\FERRAMENTAS\AutoMetaAPOLLO\popup.html`

**[B3] — Indicador de Status por Plataforma na Extensão**
- O QUE FAZER: Na extensão do postador, mostrar quais plataformas já foram postadas hoje (verde = feito, cinza = pendente) baseado em um arquivo de registro local.

**[B4] — Remoção Limpa dos Recursos Criados no "Delírio"**
- O QUE FAZER: Avaliar se o `aba_publicador.py` (servidor porta 5050) tem alguma parte útil para o B1 (hot folder). Se sim, adaptar. Se não, remover ou desativar.

**[B5] — Integração Editor → AutoFlow Apollo (Envio de Prompts)**
- O QUE FAZER: O editor Python exporta os prompts de imagem/vídeo gerados pelo agente para um arquivo `prompts_imagens.json`. O AutoFlow Apollo lê esse arquivo e pré-preenche a fila de geração. Usuário só clica "Gerar".
- NOTA: Não usa API de geração. Usa a extensão do usuário que já existe.

### BLOCO 2: ORQUESTRAÇÃO DE AGENTES (Sem Gastar API de Texto)

**[B6] — Mapa de Formatos de Canal (config por canal)**
- O QUE FAZER: Cada canal tem um `canal_config.json` que define: formato (short/longo/horizontal), agente Gemini preferido (URL do agente Web), pasta de saída, perfil de edição. O editor lê esse arquivo e ajusta tudo automaticamente.

**[B7] — Gerenciador de Canais na UI do Editor**
- O QUE FAZER: Uma aba "📺 Meus Canais" onde o usuário seleciona qual canal está editando hoje e o software carrega automaticamente as configurações (cores, fontes, TTS, pastas de B-Roll).

**[B8] — Template de Roteiro por Formato**
- O QUE FAZER: Botão "📋 Copiar Template para Agente" que gera um texto-guia que o usuário cola no agente Gemini Web. O texto já instrui o agente sobre o formato correto (short vs longo, número de cenas, etc.) sem precisar de API.

**[B9] — Importação de Roteiro do Agente**
- O QUE FAZER: Campo de texto onde o usuário cola o output do agente Gemini. O editor parseia automaticamente: extrai o texto de narração (para TTS), os prompts de imagem (para AutoFlow) e o título/descrição (para o postador). Separa tudo nos campos certos com um clique.

**[B10] — Monitor de Cota de API (Dashboard de Gastos)**
- O QUE FAZER: Um painel que lê o `historico_tokens.json` (já existe no ai_director_pipeline) e mostra: tokens gastos hoje, tokens gastos na semana, estimativa de custo em USD, alertas quando se aproximar de limites.

### BLOCO 3: INTEGRAÇÃO COM FERRAMENTAS LOCAIS (Pinokio/ComfyUI)

**[B11] — Ponte Editor → ComfyUI Local (via Pinokio)**
- O QUE FAZER: O editor exporta um JSON com os prompts de imagem. Um script Python faz chamadas à API local do ComfyUI (porta 8188) para enfileirar as gerações. As imagens geradas caem automaticamente na pasta de B-Roll do projeto.
- PRÉ-REQUISITO: ComfyUI deve estar rodando via Pinokio (`c:\pinokio`)

**[B12] — Ponte Editor → Veo/Flow (via Extensão)**
- O QUE FAZER: Similar ao B5, mas para geração de vídeo. O editor envia os prompts para a extensão AutoFlowAPOLLO via arquivo de fila. A extensão detecta e pré-preenche a interface do Google Flow/Veo.

**[B13] — Gestão de Fila de Geração de Mídia**
- O QUE FAZER: Uma aba "🎨 Fila de Mídia" no editor que lista: imagens solicitadas ao ComfyUI (status: gerando/pronto), vídeos solicitados ao Flow (status: aguardando/pronto). O usuário vê tudo centralizado.

**[B14] — Auto-organização de Pastas do Projeto**
- O QUE FAZER: Ao criar um novo projeto, o editor cria automaticamente a estrutura de pastas: `Projeto_X/narração/`, `Projeto_X/imagens/`, `Projeto_X/broll/`, `Projeto_X/output/`. Evita o usuário organizar manualmente.

**[B15] — Exportação de Projeto para Outro PC/Canal**
- O QUE FAZER: Botão "📦 Exportar Projeto" que empacota: o vídeo final, o `config.json` do canal, o `mapping.json` e o log de decisões da IA. Permite replicar o workflow em outra máquina.

### BLOCO 4: AUTOSSUFICIÊNCIA EM GERAÇÃO DE TEXTO (Fase Google)

> Contexto: As contas Google de estudante vencem em ~3 meses. Planejar alternativas agora.

**[B16] — Integração com LM Studio / Ollama Local (via Pinokio)**
- O QUE FAZER: Quando a cota do Gemini acabar, o ai_director_pipeline redireciona chamadas para um LLM local rodando no Pinokio (ex: Qwen 2.5, Gemma 3). A análise semântica continua funcionando gratuitamente.
- REFERÊNCIA: `c:\pinokio\GEMINI.md` (ver que modelos estão disponíveis)

**[B17] — Cache de Prompts (Não re-processar o mesmo roteiro)**
- O QUE FAZER: Salvar os resultados da análise do Gemini em `analise_cache.json`. Se o mesmo roteiro for renderizado novamente (re-render), reutilizar o cache sem gastar tokens.

**[B18] — Modo Agente Multi-Formato (Orchestrator)**
- O QUE FAZER: Uma interface onde o usuário descreve o vídeo em linguagem natural: "Quero um short sobre X no estilo canal Y". O sistema seleciona automaticamente o perfil de canal, o template de roteiro e as configurações de edição corretas.

**[B19] — Integração com Notion/Google Drive para Roteiros**
- O QUE FAZER: Botão "📥 Importar do Drive" que puxa um documento de texto do Google Drive (ou pasta local sincronizada) direto para o campo de roteiro do editor. Elimina abrir dois programas.

**[B20] — Documentação de Uso (Manual de Canal)**
- O QUE FAZER: Para cada canal clonado, gerar automaticamente um `MANUAL_DO_CANAL.md` com: configurações ativas, TTS cadastrado, B-Rolls disponíveis, formato padrão de vídeo, fluxo recomendado. Para o usuário nunca se perder ao voltar para um canal depois de meses.

---

## NOTAS IMPORTANTES

### Sobre o Postador (Extensão Chrome)
O postador que existe (`Postador Automatico Extensão`) é uma obra de engenharia do usuário (2 meses de trabalho).
- NÃO ALTERAR A LÓGICA DE CLIQUE (funciona, burla as defesas dos sites)
- APENAS redesenhar o visual (B2) quando chegar a hora
- O "daemon automático" adicionado na sessão anterior pode ser desativado sem impacto

### Sobre APIs de Texto (Roteiro)
- O usuário USA agentes Gemini via interface WEB (gratuito via conta de estudante)
- Cada canal tem um agente treinado com arquivos TXT/PDF pesados (contexto de canal)
- Replicar isso via API seria caro e perderia o contexto de treinamento
- Fase B só usa API de texto para ANÁLISE SEMÂNTICA (curta, barata), não para geração de roteiro

### Ordem de Prioridade
```
FASE A (TODA) → B1 → B2 → B6 → B7 → B9 → B10 → B11 → B16 → restante da Fase B
```

---

*Arquivo gerado em 2026-05-15 como guia para expansão futura.*
*Só iniciar após Fase A completamente validada em produção.*
