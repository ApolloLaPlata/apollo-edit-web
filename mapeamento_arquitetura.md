# Arquitetura de Mapeamento Multi-Agentes (Orquestração Swarm)

A geração automática de conteúdo (Vídeos, Imagens, �udios e Mapeamentos em 4 camadas) deixará de ser linear. O Apollo utilizará uma arquitetura de "Agentes Hierárquicos" (Swarm Orchestration) trabalhando em uníssono.

## O Fluxograma de Produção

1. **Agente 1: O Atendente (Criador do Receituário e Ponte Relacional)**
   - **Função:** Atuar como "Entrevistador" e ponte exclusiva de comunicação entre o Usuário e o Swarm (trabalhadores). 
   - **Ação:** Escaneia o banco de dados do usuário e gera um questionário interativo. O usuário marca as caixinhas escolhendo estilos e templates. 
   - **Sistema de Proteção (Usuário Preguiçoso):** Se o usuário não tiver nada salvo na aba Diretor ou não quiser configurar nada, a IA aplica o Fallback: *"Você não tem configurações personalizadas. Deseja usar nosso Padrão Simplificado?"* O sistema oferecerá ~3 opções genéricas (ex: Só vídeo base sem LUT, ou com legenda padrão).
   - Com as respostas, a IA cria o **Receituário** (Planta Baixa). A partir daqui, os outros robôs do Swarm assumem, isolados do usuário, focados apenas na produção em lote usando a Memória JSON coletiva.

2. **Agente 2: O Gerente (Roteirista Principal)**
   - **Função:** Entender o contexto global, o canal e as personas.
   - **Ação:** Puxa o Receituário e o expande para um **Roteiro Master**. Ele sabe o que os roteiristas técnicos precisam.

3. **Agente 3: O Analista Avançado (O Fatiador)**
   - **Função:** Dividir e Conquistar.
   - **Ação:** Pega o Roteiro Master e o quebra em dezenas de micro-tarefas altamente especializadas (Ex: "Fazer prompt visual para cena 1", "Fazer configuração de LUT para cena 2", "Dividir bloco de Lip-Sync no áudio 3").
   - **Envio:** Despacha essas fatias para a "Fazenda de Renderização Cognitiva" (Os Minions).

4. **Swarm: Chatbots Mini Econômicos (Os Minions)**
   - **Função:** Força bruta e baixo custo computacional.
   - **Ação:** Dezenas de micro-IAs rodam em paralelo. Cada uma recebe um JSON pequeno, preenche o micro-trabalho (ex: apenas a Cena 4) e devolve. Elas não têm visão do todo, apenas do seu escopo para não alucinarem.

5. **Agente 4: O Corretor de Congruência (QA / Quality Assurance)**
   - **Função:** Garantir a matemática e lógica temporal.
   - **Ação:** Puxa todos os resultados dos Minions e monta a Timeline. Ele verifica: *O tempo do áudio da Cena 1 bate com o vídeo gerado? O Lip-sync foi colocado no segundo correto e não cortou o narrador no meio de uma frase?*
   - **Loop:** Se houver erro crasso de incongruência de tempo, ele manda o pedaço com defeito voltar para o Gerente refazer. Se estiver perfeito, ele "Empacota" tudo nos **Metadados do Pack** e entrega finalizado para a �rea de Transferência do usuário (UI).

## 🛡� Regra de Ouro: Contexto Semântico do Diretor (User Background)
Para evitar que a IA faça escolhas ruins de direção de arte (ex: botar uma cena calma com transição agressiva, ou usar um template de "câmera facecam" em uma paisagem), o sistema exige **Metadados Semânticos** criados pelo usuário.
* **Aba Diretor:** Toda Configuração (LUTs, transições) ou Template Gráfico (molduras, posições) salvo pelo usuário **deve** conter uma breve descrição de intenção. Ex: *"Template A: Foco no narrador reagindo no canto direito"*, *"Config B: Clima tenso e escuro"*.
* **Consciência de Elenco:** O Receituário inicial deve obrigatoriamente questionar se o projeto possui um Narrador em Vídeo (Facecam) ou apenas voz. 
* **O Casamento Perfeito:** Quando o *Agente Fatiador* for escolher qual Template de Lip Sync usar, ele vai ler o banco de dados de Templates do usuário e fará o "Match Semântico" entre o que a cena pede e a descrição que o usuário deixou. Se o vídeo ficar ruim, a culpa será da falta de metadados, e não de uma alucinação da IA.

## Arquivos de Memória e Referência
* Todo chatbot possui acesso a um Banco de Dados de Memória JSON Coletiva. Isso permite que um Roteirista saiba qual foi o estilo usado na receita anterior e mantenha a consistência do canal.


## A Interface do Mapeamento (Mapeador Manual e Timeline)
A construção do mapeamento em 4 camadas que o Swarm realiza ganha vida na ferramenta **Mapeador Manual** (agora consolidada nos Equipamentos da interface principal). Ela permite que o usuário atue em dois formatos:
1. **Intervenção Manual:** Arrastando os \Quadradinhos Mágicos\ da sua **�rea de Transferência/Bagageiro** diretamente para os slots da timeline visual, ajustando duração de Vídeo, LUTs e Narração na mão.
2. **Revisão Visual:** Se o Swarm realizou todo o trabalho e o *Agente 4 (QA)* empacotou com sucesso, o usuário abre o Mapeador Manual apenas para revisar a conguência dos blocos injetados e, em seguida, enviar para a Fila de Render.

---
## [ATUALIZAÇÃO DE ARQUITETURA - AGENTES DE PERFORMANCE E MARKETING] (Data: 07/06/2026)

**1. Scraper de Preços Autônomo (pricing_scraper_agent.py):**
- Vasculha a API do OpenRouter em busca de novos modelos de IA.
- Cadastra novos modelos diretamente com status 'Ativo' (Autonomia Total).
- Captura Rate Limits (TPM/RPM) e atualiza preços de input/output dinamicamente.

**2. Gestor Financeiro / Analista de Mercado:**
- Motor de Precificação Dinâmica integrado à tabela models_pricing através da coluna margin_multiplier.
- Calcula o Custo da Gasolina baseado na demanda (se um modelo está ocioso, a margem cai para 10%; se está concorrido, sobe até 100%).

**3. Diretor de Marketing (marketing_agent.py):**
- Observa as ações do Diretor Financeiro.
- Gera chamadas publicitárias HTML/CSS (Gradients, Emojis, Cyberpunk) usando LLM via OpenRouter.
- Integração preparada para APIs de Imagem Reais (DALL-E 3 / fal.ai).
- Salva anúncios criados na tabela d_campaigns.

**4. Gestor de Tráfego AI (traffic_manager_agent.py):**
- Monitora os endpoints de telemetria criados no servidor_web.py (/view e /click).
- Calcula o CTR (Click-Through Rate) dos banners injetados no sistema.
- Desativa campanhas de baixa performance (CTR < 0.5% após 200 views).

**5. Sistema de Rotação de Anúncios UI (noticias_scripts.html):**
- Implementação de um rodízio Javascript que puxa campanhas ativas.
- Alternância visual a cada 30 segundos, disparando telemetria em background sem necessitar de recarregamento da página.



## A Interface do Mapeamento (Mapeador Manual e Timeline)
A construção do mapeamento em 4 camadas que o Swarm realiza ganha vida na ferramenta **Mapeador Manual** (agora consolidada nos Equipamentos da interface principal). Ela permite que o usuário atue em dois formatos:
1. **Intervenção Manual:** Arrastando os \Quadradinhos Mágicos\ da sua **�rea de Transferência/Bagageiro** diretamente para os slots da timeline visual, ajustando duração de Vídeo, LUTs e Narração na mão.
2. **Revisão Visual:** Se o Swarm realizou todo o trabalho e o *Agente 4 (QA)* empacotou com sucesso, o usuário abre o Mapeador Manual apenas para revisar a conguência dos blocos injetados e, em seguida, enviar para a Fila de Render.

---
## [ATUALIZAÇÃO DE ARQUITETURA - AGENTES DE PERFORMANCE E MARKETING] (Data: 07/06/2026)

**1. Scraper de Preços Autônomo (pricing_scraper_agent.py):**
- Vasculha a API do OpenRouter em busca de novos modelos de IA.
- Cadastra novos modelos diretamente com status 'Ativo' (Autonomia Total).
- Captura Rate Limits (TPM/RPM) e atualiza preços de input/output dinamicamente.

**2. Gestor Financeiro / Analista de Mercado:**
- Motor de Precificação Dinâmica integrado à tabela models_pricing através da coluna margin_multiplier.
- Calcula o Custo da Gasolina baseado na demanda (se um modelo está ocioso, a margem cai para 10%; se está concorrido, sobe até 100%).

**3. Diretor de Marketing (marketing_agent.py):**
- Observa as ações do Diretor Financeiro.
- Gera chamadas publicitárias HTML/CSS (Gradients, Emojis, Cyberpunk) usando LLM via OpenRouter.
- Integração preparada para APIs de Imagem Reais (DALL-E 3 / fal.ai).
- Salva anúncios criados na tabela  d_campaigns.

**4. Gestor de Tráfego AI (traffic_manager_agent.py):**
- Monitora os endpoints de telemetria criados no servidor_web.py (/view e /click).
- Calcula o CTR (Click-Through Rate) dos banners injetados no sistema.
- Desativa campanhas de baixa performance (CTR < 0.5% após 200 views).

**5. Sistema de Rotação de Anúncios UI (noticias_scripts.html):**
- Implementação de um rodízio Javascript que puxa campanhas ativas.
- Alternância visual a cada 30 segundos, disparando telemetria em background sem necessitar de recarregamento da página.

*Nota Técnica: Todos os planos de implementação, walkthroughs e documentos criados por IA estão agora salvos localmente na pasta /docs/arquivos_ia/ dentro da base de código.*

---
## [DIRETRIZ DE ARQUITETURA AVANÇADA: O ROTEADOR GATEWAY LLM] (Data: 07/06/2026)

**O Problema do 'Corta Tesouro' e Roteamento Inteligente:**
Conforme definido pelo Diretor Geral, a arquitetura futura de roteamento de Inteligência Artificial da Apollo não será apenas baseada em strings fixas ('high' ou 'low'). O sistema adotará ### 5. O Gateway Triador (LLM Routing)
A plataforma gerencia seus custos de I.A. através de um roteador cognitivo (`agent_core.py`):
- **O Roteador (Corta-Tesouro):** Todo input de usuário passa primeiro por um modelo gratuito/rápido (Llama 3 ou Claude Haiku). Esse modelo avalia a complexidade do pedido.
- **Regra de Negócio (Nível Usuário):** Absolutamente TODOS os chatbots, assistentes e interfaces voltadas para o usuário final (como o WPP Bot ou os Copilotos) devem **por padrão** utilizar o modelo que aceita mais requisições pelo menor preço possível (Llama 3 Local ou APIs gratuitas). 
- **Modelos Premium (GPT-4o, Claude Opus):** Estritamente reservados para chamadas administrativas (Diretoria/Manager) ou para usuários que estejam pagando (via Gastos de Cristais/Assinaturas). O uso indiscriminado de LLMs caros para usuários grátis é estritamente proibido. para enxugar os tokens.
4. **Despacho Final:**
   - Se for simples: O próprio Porteiro (ou outro modelo free) responde e finaliza a tarefa. Custo Zero.
   - Se for complexo: O Porteiro encaminha a requisição limpa e otimizada (com poucos tokens) para a Elite (ChatGPT-4o, Grok 3, Gemini 3.5 Pro, Claude 4.6).

**Vantagem Competitiva:**
Essa arquitetura garante lucro absoluto. Nunca gastaremos 1 centavo de dólar em tarefas triviais, e as tarefas críticas receberão a inteligência máxima sem o desperdício de contexto inchado.

---
## [NOVA DIRETRIZ: GESTÃO DE ARMAZENAMENTO E MERCADO P2P] (Data: 07/06/2026)

Para evitar a falência do sistema de nuvem devido ao alto custo de armazenamento de templates de vídeo HD transparentes (ex: arquivos de 15GB), foram definidas as seguintes políticas:

1. **Lixeiro Automático de 24h (Garbage Collector):** 
A Apollo NÃO é um serviço de hospedagem vitalício. Todos os arquivos de renderização temporários e vídeos finais em MP4 hospedados em `/static/renders/` possuem um tempo de vida estrito de 24 horas. Após esse período, um Cron Job limpa o HD automaticamente.

2. **Mercado P2P Descentralizado (External Hosting):**
Usuários podem vender "Templates HD" na loja da plataforma em troca de Cristais. No entanto, o sistema Apollo só hospeda o "Esqueleto" (.json de configuração) e um thumbnail/preview leve. O arquivo pesado do template **obrigatoriamente** deve ser hospedado pelo criador em serviços externos de nuvem (Google Drive, Dropbox, Mega). O sistema apenas transaciona o acesso/link ao comprador.

3. **Mochila (Franquia de Tráfego Mensal):**
Para evitar que usuários mal-intencionados driblem o "Lixeiro de 24h" apagando e subindo arquivos de 15GB diariamente (o que estouraria o custo de Bandwidth/Egress na AWS/GCP), contas gratuitas possuem uma "Mochila" com limite fixo de Tráfego de Upload/Download mensal (Ex: 5GB ou 10GB de bagagem gratuita). Exceder esse limite para carregar mais peso na viagem exige a compra de Cotas Extras via Cristais ou upgrade para plano Pro, eliminando o abuso do sistema. O "Bagageiro" temporário de 24h é gratuito, mas o ato de *transitar* os arquivos até ele consome o peso da Mochila.

4. **Mercado P2P Fechado (Safe Mode) e Anti-Lavagem de Dinheiro:**
- **Zero Arquivos Externos:** É estritamente proibida a venda de links do Google Drive, Mega ou arquivos pesados (.mp4, .zip) no Mercado P2P. Isso elimina 100% o risco de distribuição de Malwares, material ilícito e "Golpes de Link Vazio".
- **Comércio Exclusivo de "Cérebros":** Os usuários só podem vender Arquivos Nativos da Apollo (.json textuais). Exemplos: Roteiristas Customizados, Presets de Edição de Timeline, LUTs matemáticos. Como são arquivos nativos, a instalação na conta do comprador é *imediata* e *100% segura*.
- **Prevenção de Lavagem via Banda de Preços:** A plataforma mantém uma economia livre e descentralizada (sem burocracia de documentos KYC para sacar). Para impedir lavagem de dinheiro, o sistema impõe limites matemáticos estritos de venda: O *Preço Mínimo* é o Custo Base + Taxa da Apollo (evitando dumping); O *Preço Máximo (Teto)* é limitado a 100% de Margem de Lucro sobre o custo. Isso inviabiliza a movimentação de fortunas ilícitas num único item.
- **O Xerife do Mercado (Market Auditor AI):** Um agente autônomo específico (Agente 6) fiscaliza o Mercado P2P 24 horas por dia. Se o Xerife detectar padrões de lavagem (Ex: Usuário A compra 50 itens de preço máximo do Usuário B em poucas horas; Contas recém-criadas transacionando teto máximo), a IA congela automaticamente as carteiras envolvidas e bloqueia os saques até uma auditoria manual, mantendo a plataforma segura sem intervenção humana constante.

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

1. **Script de Orquestração:** ackend/tests/test_multipass_direct.py
2. **Método de Execução:** Execução via RPC Direta (modal run test_multipass_direct.py). NUNCA usar requisições autônomas via roteador HTTP (
equests.post), pois isso força reinicializações a frio duplas no servidor da Modal, explodindo o tempo para quase 9 minutos.
3. **Workflows ComfyUI (Os arquivos Intocáveis):**
   - **Geração Base:** pollo_flux2_klein.json (Gera o cenário sem personagens).
   - **Geração Inpaint (Multi-pass):** 10resultado_3_personagens_CHAINED_klein.json. Este arquivo roda repetidas vezes (loop nativo no python) inserindo um personagem por vez sobre a mesma imagem usando ReferenceLatent.
4. **O Segredo do Text-Locking:** O segredo para que os rostos não se fundam (Efeito Quimera) nem gerem pessoas aleatórias não é usar PuLID nem Máscaras Regionais. A solução é a redundância textual. O LLM deve receber **descrições fotorealistas idênticas às fotos** (cabelo, barba, cor de roupa, expressão). Se o prompt de texto for genérico (ex: 'Person 1, a man'), o modelo ignora a foto e desenha um estranho. Prompts maciços e descritivos *travam* a identidade na referência da imagem.
