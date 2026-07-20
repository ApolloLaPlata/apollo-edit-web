# Arquitetura de Mapeamento Multi-Agentes (OrquestraÃ§Ã£o Swarm)

A geraÃ§Ã£o automÃ¡tica de conteÃºdo (VÃ­deos, Imagens, Ã�udios e Mapeamentos em 4 camadas) deixarÃ¡ de ser linear. O Apollo utilizarÃ¡ uma arquitetura de "Agentes HierÃ¡rquicos" (Swarm Orchestration) trabalhando em unÃ­ssono.

## O Fluxograma de ProduÃ§Ã£o

1. **Agente 1: O Atendente (Criador do ReceituÃ¡rio e Ponte Relacional)**
   - **FunÃ§Ã£o:** Atuar como "Entrevistador" e ponte exclusiva de comunicaÃ§Ã£o entre o UsuÃ¡rio e o Swarm (trabalhadores). 
   - **AÃ§Ã£o:** Escaneia o banco de dados do usuÃ¡rio e gera um questionÃ¡rio interativo. O usuÃ¡rio marca as caixinhas escolhendo estilos e templates. 
   - **Sistema de ProteÃ§Ã£o (UsuÃ¡rio PreguiÃ§oso):** Se o usuÃ¡rio nÃ£o tiver nada salvo na aba Diretor ou nÃ£o quiser configurar nada, a IA aplica o Fallback: *"VocÃª nÃ£o tem configuraÃ§Ãµes personalizadas. Deseja usar nosso PadrÃ£o Simplificado?"* O sistema oferecerÃ¡ ~3 opÃ§Ãµes genÃ©ricas (ex: SÃ³ vÃ­deo base sem LUT, ou com legenda padrÃ£o).
   - Com as respostas, a IA cria o **ReceituÃ¡rio** (Planta Baixa). A partir daqui, os outros robÃ´s do Swarm assumem, isolados do usuÃ¡rio, focados apenas na produÃ§Ã£o em lote usando a MemÃ³ria JSON coletiva.

2. **Agente 2: O Gerente (Roteirista Principal)**
   - **FunÃ§Ã£o:** Entender o contexto global, o canal e as personas.
   - **AÃ§Ã£o:** Puxa o ReceituÃ¡rio e o expande para um **Roteiro Master**. Ele sabe o que os roteiristas tÃ©cnicos precisam.

3. **Agente 3: O Analista AvanÃ§ado (O Fatiador)**
   - **FunÃ§Ã£o:** Dividir e Conquistar.
   - **AÃ§Ã£o:** Pega o Roteiro Master e o quebra em dezenas de micro-tarefas altamente especializadas (Ex: "Fazer prompt visual para cena 1", "Fazer configuraÃ§Ã£o de LUT para cena 2", "Dividir bloco de Lip-Sync no Ã¡udio 3").
   - **Envio:** Despacha essas fatias para a "Fazenda de RenderizaÃ§Ã£o Cognitiva" (Os Minions).

4. **Swarm: Chatbots Mini EconÃ´micos (Os Minions)**
   - **FunÃ§Ã£o:** ForÃ§a bruta e baixo custo computacional.
   - **AÃ§Ã£o:** Dezenas de micro-IAs rodam em paralelo. Cada uma recebe um JSON pequeno, preenche o micro-trabalho (ex: apenas a Cena 4) e devolve. Elas nÃ£o tÃªm visÃ£o do todo, apenas do seu escopo para nÃ£o alucinarem.

5. **Agente 4: O Corretor de CongruÃªncia (QA / Quality Assurance)**
   - **FunÃ§Ã£o:** Garantir a matemÃ¡tica e lÃ³gica temporal.
   - **AÃ§Ã£o:** Puxa todos os resultados dos Minions e monta a Timeline. Ele verifica: *O tempo do Ã¡udio da Cena 1 bate com o vÃ­deo gerado? O Lip-sync foi colocado no segundo correto e nÃ£o cortou o narrador no meio de uma frase?*
   - **Loop:** Se houver erro crasso de incongruÃªncia de tempo, ele manda o pedaÃ§o com defeito voltar para o Gerente refazer. Se estiver perfeito, ele "Empacota" tudo nos **Metadados do Pack** e entrega finalizado para a Ã�rea de TransferÃªncia do usuÃ¡rio (UI).

## ðŸ›¡ï¸� Regra de Ouro: Contexto SemÃ¢ntico do Diretor (User Background)
Para evitar que a IA faÃ§a escolhas ruins de direÃ§Ã£o de arte (ex: botar uma cena calma com transiÃ§Ã£o agressiva, ou usar um template de "cÃ¢mera facecam" em uma paisagem), o sistema exige **Metadados SemÃ¢nticos** criados pelo usuÃ¡rio.
* **Aba Diretor:** Toda ConfiguraÃ§Ã£o (LUTs, transiÃ§Ãµes) ou Template GrÃ¡fico (molduras, posiÃ§Ãµes) salvo pelo usuÃ¡rio **deve** conter uma breve descriÃ§Ã£o de intenÃ§Ã£o. Ex: *"Template A: Foco no narrador reagindo no canto direito"*, *"Config B: Clima tenso e escuro"*.
* **ConsciÃªncia de Elenco:** O ReceituÃ¡rio inicial deve obrigatoriamente questionar se o projeto possui um Narrador em VÃ­deo (Facecam) ou apenas voz. 
* **O Casamento Perfeito:** Quando o *Agente Fatiador* for escolher qual Template de Lip Sync usar, ele vai ler o banco de dados de Templates do usuÃ¡rio e farÃ¡ o "Match SemÃ¢ntico" entre o que a cena pede e a descriÃ§Ã£o que o usuÃ¡rio deixou. Se o vÃ­deo ficar ruim, a culpa serÃ¡ da falta de metadados, e nÃ£o de uma alucinaÃ§Ã£o da IA.

## Arquivos de MemÃ³ria e ReferÃªncia
* Todo chatbot possui acesso a um Banco de Dados de MemÃ³ria JSON Coletiva. Isso permite que um Roteirista saiba qual foi o estilo usado na receita anterior e mantenha a consistÃªncia do canal.


## A Interface do Mapeamento (Mapeador Manual e Timeline)
A construÃ§Ã£o do mapeamento em 4 camadas que o Swarm realiza ganha vida na ferramenta **Mapeador Manual** (agora consolidada nos Equipamentos da interface principal). Ela permite que o usuÃ¡rio atue em dois formatos:
1. **IntervenÃ§Ã£o Manual:** Arrastando os \Quadradinhos MÃ¡gicos\ da sua **Ã�rea de TransferÃªncia/Bagageiro** diretamente para os slots da timeline visual, ajustando duraÃ§Ã£o de VÃ­deo, LUTs e NarraÃ§Ã£o na mÃ£o.
2. **RevisÃ£o Visual:** Se o Swarm realizou todo o trabalho e o *Agente 4 (QA)* empacotou com sucesso, o usuÃ¡rio abre o Mapeador Manual apenas para revisar a conguÃªncia dos blocos injetados e, em seguida, enviar para a Fila de Render.

---
## [ATUALIZAÃ‡ÃƒO DE ARQUITETURA - AGENTES DE PERFORMANCE E MARKETING] (Data: 07/06/2026)

**1. Scraper de PreÃ§os AutÃ´nomo (pricing_scraper_agent.py):**
- Vasculha a API do OpenRouter em busca de novos modelos de IA.
- Cadastra novos modelos diretamente com status 'Ativo' (Autonomia Total).
- Captura Rate Limits (TPM/RPM) e atualiza preÃ§os de input/output dinamicamente.

**2. Gestor Financeiro / Analista de Mercado:**
- Motor de PrecificaÃ§Ã£o DinÃ¢mica integrado Ã  tabela models_pricing atravÃ©s da coluna margin_multiplier.
- Calcula o Custo da Gasolina baseado na demanda (se um modelo estÃ¡ ocioso, a margem cai para 10%; se estÃ¡ concorrido, sobe atÃ© 100%).

**3. Diretor de Marketing (marketing_agent.py):**
- Observa as aÃ§Ãµes do Diretor Financeiro.
- Gera chamadas publicitÃ¡rias HTML/CSS (Gradients, Emojis, Cyberpunk) usando LLM via OpenRouter.
- IntegraÃ§Ã£o preparada para APIs de Imagem Reais (DALL-E 3 / fal.ai).
- Salva anÃºncios criados na tabela d_campaigns.

**4. Gestor de TrÃ¡fego AI (traffic_manager_agent.py):**
- Monitora os endpoints de telemetria criados no servidor_web.py (/view e /click).
- Calcula o CTR (Click-Through Rate) dos banners injetados no sistema.
- Desativa campanhas de baixa performance (CTR < 0.5% apÃ³s 200 views).

**5. Sistema de RotaÃ§Ã£o de AnÃºncios UI (noticias_scripts.html):**
- ImplementaÃ§Ã£o de um rodÃ­zio Javascript que puxa campanhas ativas.
- AlternÃ¢ncia visual a cada 30 segundos, disparando telemetria em background sem necessitar de recarregamento da pÃ¡gina.



## A Interface do Mapeamento (Mapeador Manual e Timeline)
A construÃ§Ã£o do mapeamento em 4 camadas que o Swarm realiza ganha vida na ferramenta **Mapeador Manual** (agora consolidada nos Equipamentos da interface principal). Ela permite que o usuÃ¡rio atue em dois formatos:
1. **IntervenÃ§Ã£o Manual:** Arrastando os \Quadradinhos MÃ¡gicos\ da sua **Ã�rea de TransferÃªncia/Bagageiro** diretamente para os slots da timeline visual, ajustando duraÃ§Ã£o de VÃ­deo, LUTs e NarraÃ§Ã£o na mÃ£o.
2. **RevisÃ£o Visual:** Se o Swarm realizou todo o trabalho e o *Agente 4 (QA)* empacotou com sucesso, o usuÃ¡rio abre o Mapeador Manual apenas para revisar a conguÃªncia dos blocos injetados e, em seguida, enviar para a Fila de Render.

---
## [ATUALIZAÃ‡ÃƒO DE ARQUITETURA - AGENTES DE PERFORMANCE E MARKETING] (Data: 07/06/2026)

**1. Scraper de PreÃ§os AutÃ´nomo (pricing_scraper_agent.py):**
- Vasculha a API do OpenRouter em busca de novos modelos de IA.
- Cadastra novos modelos diretamente com status 'Ativo' (Autonomia Total).
- Captura Rate Limits (TPM/RPM) e atualiza preÃ§os de input/output dinamicamente.

**2. Gestor Financeiro / Analista de Mercado:**
- Motor de PrecificaÃ§Ã£o DinÃ¢mica integrado Ã  tabela models_pricing atravÃ©s da coluna margin_multiplier.
- Calcula o Custo da Gasolina baseado na demanda (se um modelo estÃ¡ ocioso, a margem cai para 10%; se estÃ¡ concorrido, sobe atÃ© 100%).

**3. Diretor de Marketing (marketing_agent.py):**
- Observa as aÃ§Ãµes do Diretor Financeiro.
- Gera chamadas publicitÃ¡rias HTML/CSS (Gradients, Emojis, Cyberpunk) usando LLM via OpenRouter.
- IntegraÃ§Ã£o preparada para APIs de Imagem Reais (DALL-E 3 / fal.ai).
- Salva anÃºncios criados na tabela  d_campaigns.

**4. Gestor de TrÃ¡fego AI (traffic_manager_agent.py):**
- Monitora os endpoints de telemetria criados no servidor_web.py (/view e /click).
- Calcula o CTR (Click-Through Rate) dos banners injetados no sistema.
- Desativa campanhas de baixa performance (CTR < 0.5% apÃ³s 200 views).

**5. Sistema de RotaÃ§Ã£o de AnÃºncios UI (noticias_scripts.html):**
- ImplementaÃ§Ã£o de um rodÃ­zio Javascript que puxa campanhas ativas.
- AlternÃ¢ncia visual a cada 30 segundos, disparando telemetria em background sem necessitar de recarregamento da pÃ¡gina.

*Nota TÃ©cnica: Todos os planos de implementaÃ§Ã£o, walkthroughs e documentos criados por IA estÃ£o agora salvos localmente na pasta /docs/arquivos_ia/ dentro da base de cÃ³digo.*

---
## [DIRETRIZ DE ARQUITETURA AVANÃ‡ADA: O ROTEADOR GATEWAY LLM] (Data: 07/06/2026)

**O Problema do 'Corta Tesouro' e Roteamento Inteligente:**
Conforme definido pelo Diretor Geral, a arquitetura futura de roteamento de InteligÃªncia Artificial da Apollo nÃ£o serÃ¡ apenas baseada em strings fixas ('high' ou 'low'). O sistema adotarÃ¡ ### 5. O Gateway Triador (LLM Routing)
A plataforma gerencia seus custos de I.A. atravÃ©s de um roteador cognitivo (`agent_core.py`):
- **O Roteador (Corta-Tesouro):** Todo input de usuÃ¡rio passa primeiro por um modelo gratuito/rÃ¡pido (Llama 3 ou Claude Haiku). Esse modelo avalia a complexidade do pedido.
- **Regra de NegÃ³cio (NÃ­vel UsuÃ¡rio):** Absolutamente TODOS os chatbots, assistentes e interfaces voltadas para o usuÃ¡rio final (como o WPP Bot ou os Copilotos) devem **por padrÃ£o** utilizar o modelo que aceita mais requisiÃ§Ãµes pelo menor preÃ§o possÃ­vel (Llama 3 Local ou APIs gratuitas). 
- **Modelos Premium (GPT-4o, Claude Opus):** Estritamente reservados para chamadas administrativas (Diretoria/Manager) ou para usuÃ¡rios que estejam pagando (via Gastos de Cristais/Assinaturas). O uso indiscriminado de LLMs caros para usuÃ¡rios grÃ¡tis Ã© estritamente proibido. para enxugar os tokens.
4. **Despacho Final:**
   - Se for simples: O prÃ³prio Porteiro (ou outro modelo free) responde e finaliza a tarefa. Custo Zero.
   - Se for complexo: O Porteiro encaminha a requisiÃ§Ã£o limpa e otimizada (com poucos tokens) para a Elite (ChatGPT-4o, Grok 3, Gemini 3.5 Pro, Claude 4.6).

**Vantagem Competitiva:**
Essa arquitetura garante lucro absoluto. Nunca gastaremos 1 centavo de dÃ³lar em tarefas triviais, e as tarefas crÃ­ticas receberÃ£o a inteligÃªncia mÃ¡xima sem o desperdÃ­cio de contexto inchado.

---
## [NOVA DIRETRIZ: GESTÃƒO DE ARMAZENAMENTO E MERCADO P2P] (Data: 07/06/2026)

Para evitar a falÃªncia do sistema de nuvem devido ao alto custo de armazenamento de templates de vÃ­deo HD transparentes (ex: arquivos de 15GB), foram definidas as seguintes polÃ­ticas:

1. **Lixeiro AutomÃ¡tico de 24h (Garbage Collector):** 
A Apollo NÃƒO Ã© um serviÃ§o de hospedagem vitalÃ­cio. Todos os arquivos de renderizaÃ§Ã£o temporÃ¡rios e vÃ­deos finais em MP4 hospedados em `/static/renders/` possuem um tempo de vida estrito de 24 horas. ApÃ³s esse perÃ­odo, um Cron Job limpa o HD automaticamente.

2. **Mercado P2P Descentralizado (External Hosting):**
UsuÃ¡rios podem vender "Templates HD" na loja da plataforma em troca de Cristais. No entanto, o sistema Apollo sÃ³ hospeda o "Esqueleto" (.json de configuraÃ§Ã£o) e um thumbnail/preview leve. O arquivo pesado do template **obrigatoriamente** deve ser hospedado pelo criador em serviÃ§os externos de nuvem (Google Drive, Dropbox, Mega). O sistema apenas transaciona o acesso/link ao comprador.

3. **Mochila (Franquia de TrÃ¡fego Mensal):**
Para evitar que usuÃ¡rios mal-intencionados driblem o "Lixeiro de 24h" apagando e subindo arquivos de 15GB diariamente (o que estouraria o custo de Bandwidth/Egress na AWS/GCP), contas gratuitas possuem uma "Mochila" com limite fixo de TrÃ¡fego de Upload/Download mensal (Ex: 5GB ou 10GB de bagagem gratuita). Exceder esse limite para carregar mais peso na viagem exige a compra de Cotas Extras via Cristais ou upgrade para plano Pro, eliminando o abuso do sistema. O "Bagageiro" temporÃ¡rio de 24h Ã© gratuito, mas o ato de *transitar* os arquivos atÃ© ele consome o peso da Mochila.

4. **Mercado P2P Fechado (Safe Mode) e Anti-Lavagem de Dinheiro:**
- **Zero Arquivos Externos:** Ã‰ estritamente proibida a venda de links do Google Drive, Mega ou arquivos pesados (.mp4, .zip) no Mercado P2P. Isso elimina 100% o risco de distribuiÃ§Ã£o de Malwares, material ilÃ­cito e "Golpes de Link Vazio".
- **ComÃ©rcio Exclusivo de "CÃ©rebros":** Os usuÃ¡rios sÃ³ podem vender Arquivos Nativos da Apollo (.json textuais). Exemplos: Roteiristas Customizados, Presets de EdiÃ§Ã£o de Timeline, LUTs matemÃ¡ticos. Como sÃ£o arquivos nativos, a instalaÃ§Ã£o na conta do comprador Ã© *imediata* e *100% segura*.
- **PrevenÃ§Ã£o de Lavagem via Banda de PreÃ§os:** A plataforma mantÃ©m uma economia livre e descentralizada (sem burocracia de documentos KYC para sacar). Para impedir lavagem de dinheiro, o sistema impÃµe limites matemÃ¡ticos estritos de venda: O *PreÃ§o MÃ­nimo* Ã© o Custo Base + Taxa da Apollo (evitando dumping); O *PreÃ§o MÃ¡ximo (Teto)* Ã© limitado a 100% de Margem de Lucro sobre o custo. Isso inviabiliza a movimentaÃ§Ã£o de fortunas ilÃ­citas num Ãºnico item.
- **O Xerife do Mercado (Market Auditor AI):** Um agente autÃ´nomo especÃ­fico (Agente 6) fiscaliza o Mercado P2P 24 horas por dia. Se o Xerife detectar padrÃµes de lavagem (Ex: UsuÃ¡rio A compra 50 itens de preÃ§o mÃ¡ximo do UsuÃ¡rio B em poucas horas; Contas recÃ©m-criadas transacionando teto mÃ¡ximo), a IA congela automaticamente as carteiras envolvidas e bloqueia os saques atÃ© uma auditoria manual, mantendo a plataforma segura sem intervenÃ§Ã£o humana constante.

---
## V. A Infraestrutura Serverless Privada (A Frota Lightning ⚡)

A arquitetura do Apollo pivotou radicalmente a função do provedor **Lightning AI ($60/mês)**. Ao invés de usá-lo como provedor de geração pesada de Imagem (Flux) e incorrer em altos custos de Storage, o Lightning agora funciona como um **Swarm (Enxame) de Micro-Máquinas Específicas**.

Toda a geração de imagem/vídeo pesada foi transferida para provedores terceirizados (Modal/RunPod/OpenRouter). O Lightning é exclusivo para o "Cérebro Tagarela" (LLM/TTS/STT) e Scripts rápidos.

### 1. Separação em Microsserviços e Redução de Storage
Para garantir tempos de boot incríveis e multiplicar o número de instâncias dentro do orçamento, instalamos modelos levíssimos (ex: Whisper de 1GB, Piper/VITS de 2GB) sem UI pesada.
- **Divisão de Máquinas:**
  - *O Enxame de Chatbots Grátis (CPUs Gratuitas):* Máquinas de custo zero (Free CPU de 4 núcleos) mantidas online ou em cold-boot para atender ao Modo Gratuito do Mascote. O TTS roda na CPU, demorando mais, mas mantendo custo zero.
  - *Os Chatbots Nitro (GPU T4):* Dedicados aos usuários do modo Premium (compram "Nitro" com Cristais). Respostas quase instantâneas.
  - *Máquinas de Edição Bruta (FFmpeg):* Processamento instantâneo de recortes de vídeo, concatenações e manipulação de mídia em scripts Python super leves.

### 2. O Roteador Dinâmico (Smart Router e Nitro Master)
A Apollo atua como Roteadora Inteligente das requisições, aplicando a lógica do "Chat do Pobre vs Chat do Ricasso":
1. O usuário manda áudio/texto para o Chatbot.
2. O Backend do Apollo (via `lightning_mascot_api.py`) lê a permissão e os fundos de Cristais do usuário.
3. Se o usuário tem o "Nitro T4" ou "Nitro Master" habilitado, a requisição fura-fila e vai para uma máquina GPU potente (Cold-Boot ou já warm) e a plataforma desconta Cristais do usuário.
4. Se for free, o fluxo entra nas máquinas CPU compartilhadas do Enxame Grátis.
Isso garante a sobrevivência econômica da plataforma, permitindo centenas de chamadas escaláveis sem falência de cloud costs.

---
## [MAPEAMENTO DA API CENTRAL DE INFERÊNCIA (LIGHTNING AI)] (Data: 08/06/2026)

**A GRANDE DESCOBERTA:** 
Não precisamos criar dezenas de "Agentes" isolados no painel da Lightning e capturar URLs diferentes. A Lightning AI provê uma **API Universal Padrão OpenAI**. 
Com uma única Chave de API, podemos chamar *QUALQUER* modelo trocando apenas a string do parâmetro model.

**Endpoint Universal:** https://lightning.ai/api/v1/chat/completions
**Formato:** Idêntico à API da OpenAI (Permite usar a biblioteca oficial openai do Python/Node).

### Exemplos de Chamada de Produção (Guardados para o Apollo):

**Python (Biblioteca OpenAI Oficial):**
`python
from openai import OpenAI
client = OpenAI(
    base_url="https://lightning.ai/api/v1/",
    api_key="SUA_CHAVE_AQUI",
)
completion = client.chat.completions.create(
    model="openai/gpt-5", # AQUI TROCAMOS O MODELO DINAMICAMENTE
    messages=[{"role": "user", "content": "Hello, world!"}]
)
print(completion.choices[0].message.content)
`

**JavaScript (Fetch puro - Útil para painéis leves):**
`javascript
fetch("https://lightning.ai/api/v1/chat/completions", {
  method: "POST",
  headers: {
    "Authorization": "Bearer SUA_CHAVE_AQUI",
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    model: "openai/gpt-5", // TROCA-SE O MODELO AQUI
    messages: [{ role: "user", content: "Hello, world" }]
  }),
});
`

### TABELA DE MODELOS E CUSTOS (Referência para o Banco de Dados)
*(Nota: Valores parecem ser USD por 1 Milhão de Tokens - Input / Output)*

| Modelo | Provedor | Custo (In/Out) | Contexto |
| :--- | :--- | :--- | :--- |
| **nvidia-nemotron-3-ultra-550b-a55b** | Nvidia / Lightning | **.00 / .00** (GRATUITO/ZERO) | - |
| GPT 4 | OpenAI | .00 / .00 | 8K |
| GPT 4 Turbo | OpenAI | .00 / .00 | 128K |
| GPT 4o | OpenAI | .50 / .00 | 128K |
| GPT 5 | OpenAI | .25 / .00 | 400K |
| GPT 5.2 | OpenAI | .75 / .00 | 400K |
| GPT 5.4 | OpenAI | .50 / .00 | 1M |
| GPT 5.5 | OpenAI | .00 / .00 | 1M |
| Claude Opus 4 | Anthropic | .00 / .00 | 200K |
| Claude Opus 4.1 | Anthropic | .00 / .00 | 200K |
| Claude Opus 4.5 | Anthropic | .00 / .00 | 200K |
| Claude Opus 4.6 | Anthropic | .00 / .00 | 200K |
| Claude Opus 4.7 | Anthropic | .00 / .00 | 1M |
| Claude Opus 4.8 | Anthropic | .00 / .00 | 1M |
| Claude Sonnet 4 | Anthropic | .00 / .00 | 200K |
| Claude Sonnet 4.5 | Anthropic | .00 / .00 | 200K |
| Claude Sonnet 4.6 | Anthropic | .00 / .00 | 200K |
| Gemini 3.1 Pro | Google | .00 / .00 | 1M |

---


## 7. ARQUITETURA DEFINITIVA DE GERAÇÃO DE IMAGENS (FLUX MULTI-PASS / TEXT-LOCKING)
*(Registro de Ouro - 10/07/2026)*

**A LÓGICA DE INJEÇÃO (NÃO ALTERAR):**
O processo que insere múltiplos personagens (ex: 3 pessoas) em uma única imagem foi otimizado para a nuvem Modal. A única forma aceitável e rápida (~2.5 minutos) de executá-lo é através do motor nativo:

1. **Script de Orquestração:** ackend/tests/test_multipass_direct.py
2. **Método de Execução:** Execução via RPC Direta (modal run test_multipass_direct.py). NUNCA usar requisições autônomas via roteador HTTP (
equests.post), pois isso força reinicializações a frio duplas no servidor da Modal, explodindo o tempo para quase 9 minutos.
3. **Workflows ComfyUI (Os arquivos Intocáveis):**
   - **Geração Base:** pollo_flux2_klein.json (Gera o cenário sem personagens).
   - **Geração Inpaint (Multi-pass):** 10resultado_3_personagens_CHAINED_klein.json. Este arquivo roda repetidas vezes (loop nativo no python) inserindo um personagem por vez sobre a mesma imagem usando ReferenceLatent.
4. **O Segredo do Text-Locking:** O segredo para que os rostos não se fundam (Efeito Quimera) nem gerem pessoas aleatórias não é usar PuLID nem Máscaras Regionais. A solução é a redundância textual. O LLM deve receber **descrições fotorealistas idênticas às fotos** (cabelo, barba, cor de roupa, expressão). Se o prompt de texto for genérico (ex: 'Person 1, a man'), o modelo ignora a foto e desenha um estranho. Prompts maciços e descritivos *travam* a identidade na referência da imagem.
