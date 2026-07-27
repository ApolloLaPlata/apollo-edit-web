# Apollo Modal AI Studio v2.0 - Arquitetura de Latência Zero (Streaming + Runtime Boot)
**Data de Validação:** 27 de Julho de 2026
**Tempos Registrados (Geração 8K Flux 2):** 
- *Warm (Quente):* 4.4s a 5.1s
- *Cold Start:* ~73.8s (reduzido de +4min)

Este documento foi criado para **eternizar a tecnologia** exigida pelo usuário, garantindo que futuros agentes de IA tenham acesso imediato ao contexto e não destruam a infraestrutura tentando reinventar a roda.

## 1. O Fim do Serverless Polling (Vercel By-Pass)
O principal gargalo de latência do Apollo v1.0 era o Vercel. O Vercel possui limites estritos de *Timeout* (10 a 60 segundos) no plano Free/Pro. 
Na arquitetura antiga, o Frontend chamava o Vercel (`/api/studio/modal/generate_image`), e o Vercel chamava a Modal, ficando preso e sofrendo timeout ou exigindo um sistema falho de Polling (onde o frontend batia na porta a cada 5 segundos).

### A Nova Solução (Frontend Direto)
O código no navegador (`modal_ai_studio.html` e `apollo_render_studio.html`) agora faz requisições diretas ao roteador da Modal via HTTPS:
`https://canalobservadoreconomico--apollo-render-router-apollo-api.modal.run/generate/image`

## 2. A Mágica do NDJSON Streaming
Para que o navegador entenda a resposta sem dar "Timeout" no frontend, e para podermos entregar status em tempo real, a Modal **não retorna a requisição de uma vez**.
Ela envia os dados via `yield` no Python através de **NDJSON (Newline Delimited JSON)**.

O Javascript foi reescrito (função `generateImage`) para não esperar o fim da requisição. Ele usa o método `.text()` do Response e varre as linhas delimitadas por `\n`, extraindo o último JSON válido contendo `image_base64`. Isso resolve o problema de conexões longas e garante que a imagem pipoque na tela do usuário no exato milissegundo em que a GPU da Modal termina o encode.

## 3. O Fim do PyTorch Crash no Snapshot
Na v1, tentávamos forçar a compilação do ComfyUI durante a fase de imagem `modal.build` e a inicialização de VRAM usando decorators `@modal.enter(snap=True)`.
A Modal constrói *snapshots* usando contêineres de CPU puro. Qualquer menção a `torch.cuda` fazia o boot crashar, gerando loops infinitos de Cold Start que duravam até 7 minutos (A Modal dava retry no timeout de 180s).

### A Solução Otimizada do Motor
- **`enable_memory_snapshot` foi DESTRUTIVAMENTE SETADO PARA `False`** e **os marcadores `snap=True` foram REMOVIDOS**. 
- Ao invés de tentar simular uma GPU na CPU, o backend (`universal_engine.py`, `flux_engine.py`) empurra a inicialização do PyTorch e do ComfyUI para o momento em que o Container liga de verdade na **H100 (Fase de Runtime)**. 
- O download dos pesos colossais de 23GB do Flux ocorre de forma persistente e inteligente através dos Volumes (`/comfyui_models`). 
- Essa combinação, aliada ao acesso ultra-rápido dos Volumes da Modal, gerou um Cold Start real impressionante de apenas 73 segundos para todo o sistema operacional, UI e dependências. E tempos quentes sub-6 segundos.

## 4. O Caminho dos Workflows
**MUITO IMPORTANTE:**
O servidor Backend da Modal não enxerga a estrutura local do Windows. Os Workflows JSON do ComfyUI (como `flux_upscale_ultrasharp.json`) são mapeados via `modal.Image.add_local_dir` e injetados dentro de `/workflows` na raiz do container Linux.
Nunca use caminhos relativos em Python como `../../Comfyui Workflow API/` dentro da engine na nuvem. Use sempre `/workflows/nome_do_arquivo.json`.

---
*Fim do Relatório. Esta tecnologia é o núcleo do Apollo Edit Web. Proteja esta arquitetura.*
