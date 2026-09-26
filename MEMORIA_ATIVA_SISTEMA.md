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
- **Motor de Imagem (FLUX / QWEN / Z-IMAGE):** A Conta 7 (canalobservadoreconomico) é o HUB OFICIAL DESIGNADO para abrigar todos os modelos de imagem (Flux, Qwen Image, Z-Image, Hunyuan). Atualmente apenas o FLUX está rodando 100% nela; o deploy e roteamento dos demais modelos visuais estão pendentes de homologação final. NENHUMA OUTRA CONTA deve ser usada para imagem.
- **Motor TTS (Qwen):** Completamente roteado no frontend (com campo de instrução emocional) e backend (
outes_voice.py). A arquitetura envia payload com 	ext, 
ef_audio_base64 e instruct_text direto para a Modal da Conta 10. Considerado ESTÁVEL e pronto para testes exaustivos na interface do Modal AI Studio.

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
  - **Atenção**: O Hugging Face rejeita git push com arquivos binários pesados (.png, .wav, .db). Configure o .gitignore rigorosamente e instale dependências secundárias (como oto3) manualmente no 
equirements.txt.
## POLÍTICA ECONÔMICA DOS AGENTES (DIRETRIZ DE ARQUITETURA CRÍTICA) - Atualizado 2026-09-21
- **A Torneira Pingando:** O sistema Multi-Agente (TrendResearcher, Concierge, Maestro) atua em background. Para evitar o consumo silencioso de fundos reais:
  1. **Proibição do OpenRouter no Background:** Os agentes de patrulha e monitoramento de fundo estão **terminantemente proibidos** de utilizar a API do OpenRouter. O OpenRouter é restrito exclusivamente para geração de conteúdo primário (quando o usuário explicitamente clica para gerar um vídeo, roteiro ou artigo).
  2. **Uso Exclusivo da Lightning AI:** Os agentes secundários devem ser roteados sempre para as contas do Pool da Lightning AI (Contas 1 a 4). 
  3. **Event-Driven (Operação por Demanda):** A frequência de polling e patrulha dos robôs deve ser ajustada para intervalos espaçados (ex: 2x ao dia) ou operarem apenas como gatilho após a interação humana. Se o pool gratuito esgotar, os robôs devem entrar em hibernação em vez de acionar o OpenRouter.

## A ESTRUTURA JAMSTACK (AUTOBLOG)
- O Autoblog (Next.js) é o CMS.
- **Frontend (UI):** Deve residir no Vercel para escalabilidade.
- **Banco de Dados (DB):** Migrar de SQLite para um Cloud DB (Supabase ou Neon Postgres) compatível com Vercel Serverless.
- **Backend (Apollo API):** Reside no Hugging Face (ou Oracle) orquestrando o IA e fazendo chamadas ao DB remotamente.

- **[2026-09-22 18:00] [ARQUITETURA]**: Decisão do CEO: Supabase UNIFICADO (1 projeto para Apollo, Autoblog, Achadinhos, Broadcaster) e GitHub SEPARADO (1 repositório por site para salvar a cota da Vercel).
- **[2026-09-22 18:25] [BRANDING GLOBAL]**: O CEO decretou a padronização oficial do Ecossistema sob a marca Mãe APOLLO. Os projetos agora se chamam: Apollo Edit, Apollo Autoblog, Apollo Achadinhos e Apollo Broadcaster.


# =======================================================
# 🏛️ BLUEPRINT ARQUITETURAL MESTRE (APOLLO SISTEMAS) 🏛️
# =======================================================
[Data da Homologação: 2026-09-23]
O CEO e o Maestro decretaram a infraestrutura definitiva de hardware e nuvem para o ecossistema. TODOS OS AGENTES devem alinhar suas tomadas de decisão a esta topologia.

### 1. SEPARAÇÃO ZERO-TRUST (REPOSITÓRIOS E BANCOS)
Nenhum projeto compartilha Banco de Dados. Isolação Física é a Lei.
1. Apollo Edit Web (Repo Próprio / Supabase 1)
2. Apollo Pocket Director (Repo Próprio / Supabase 2)
3. Auto-Blog CMS (Repo Próprio / Supabase 3)
4. Achadinhos SaaS (Repo Próprio / Supabase 4)
5. Apollo Broadcaster (Repo Próprio / Supabase 5)
6. Apollo RMT (Repo Próprio / Supabase 6)

### 2. A MATRIX DE HARDWARE / NUVEM (LOAD BALANCING)
* **Vercel:** Camada de Apresentação visual (Frontend Next.js/React de todos os sites).
* **Supabase:** Memória Relacional exclusiva de cada projeto (Tabelas de Auth, Logs, Produtos).
* **Lightning AI:** Motor LLM exclusivo (Geração de texto, raciocínio, lógica dos bots).
* **Modal (A Fábrica de Força Bruta):** Geração de Imagem, Vídeo de IA (Sora/Luma/Flux) e **Processamento Pesado de FFmpeg**. Escalonamento infinito para aguentar picos de 100+ usuários simultâneos.
* **Hugging Face Conta 1 (16GB RAM):** Processamento Python leve/intermediário. Roda RAG, bancos vetoriais, scripts de scraping, e automações leves para poupar créditos do Modal.
* **Hugging Face Conta 2 (CDN / Armazém Gigante):** Usado como Datasets/Static Spaces para HOSPEDAGEM GRATUITA de vídeos pesados, funcionando como CDN para o Broadcaster e Apollo Edit.
* **Oracle Conta 1 (VPS Dedicada):** Exclusiva para manter o servidor NGINX/RTMP do Broadcaster de pé 24/7.
* **Oracle Conta 2 (O Maestro Orchestrator):** Máquina leve de gerência. Roda cron jobs, daemons de WhatsApp/Telegram e coordena disparos para Modal e HF.


## DIRETRIZ DE NEGÓCIOS E MONETIZAÇÃO (Atualizado 2026-09-23)
- **Modelo de Negócios (SaaS Aggregator):** O Apollo Edit atua consolidando as IAs (Vídeo, Imagem, Voz). Para evitar a armadilha do "Wrapper Death Trap" e o esmagamento de margens, o sistema deve orquestrar **Workflows Completos** (A Esteira de Produção), entregando o arquivo finalizado, e não apenas caixas de texto avulsas.
- **Sistema de Créditos (Apollo Coins):** 
  - A arquitetura do painel (Vercel) DEVE incorporar um sistema de balanceamento de créditos. 
  - Modelos pesados (Modal/Flux/Sora) consomem X moedas. Modelos leves (HF/Qwen) consomem Y moedas.
  - Ticket inicial planejado para o Dia 1: \.00 mensais.
  - Venda de pacotes "Pay-as-you-go" (Recarga de \) para usuários que esgotarem o limite mensal.


## DIRETRIZ DE DOMÍNIOS E INTERNACIONALIZAÇÃO (i18n) - [2026-09-23]
- **Isolamento de Domínios:** Confirmada a estratégia de compra de domínios puros para cada projeto (não usaremos subdomínios compartilhados para preservar o SEO de cada nicho).
- **Estratégia Global (.com e .com.br):** Cada projeto deve garantir os domínios .com.br (Tráfego PT-BR) e .com (Tráfego Internacional/Inglês).
- **O Fator Custo:** Como o ecossistema Apollo roda em infraestrutura Serverless gratuita/sob demanda (Vercel + Hugging Face + Modal), a taxa anual de domínios (~R$ 110/ano por projeto) é o **único custo fixo real** da operação, viabilizando margens de lucro extremas.
- **Arquitetura Multi-idioma (Next.js i18n):** O frontend na Vercel deve ser preparado para Internationalized Routing. O domínio .com.br forçará a renderização em português, e o .com forçará a versão global (inglês), permitindo faturar em Dólar na gringa.


## DIRETRIZ DE OPERAÇÕES E REDES SOCIAIS (A ESTRATÉGIA UMBRELLA) - [2026-09-23]
Para evitar a exaustão operacional (criar e gerenciar 20 contas de redes sociais diferentes), o Ecossistema divide-se em "Blocos de Audiência":
1. **O Bloco Corporativo (SaaS / B2B):** Apollo Edit, Apollo Pocket Director, e Apollo Achadinhos. 
   - **Operação:** Estes compartilham um ÚNICO Gmail (ex: contato.apollo@...), um ÚNICO Canal de YouTube (Marca "Apollo"), Instagram e TikTok. O público é o mesmo: criadores de conteúdo, afiliados e empreendedores. No YouTube, cada software ganha uma "Playlist" dedicada.
2. **O Bloco de Nicho (B2C / Produto Final):** Apollo RMT, AutoBlog e Broadcaster.
   - **Operação:** Estes exigem contas isoladas. Um jogador de RPG (RMT) não consome conteúdo de software SaaS. A Rádio 24h (Broadcaster) precisa de um canal dedicado exclusivo para música.
- **Conclusão:** O trabalho do Mestre reduz-se pela metade. Agrupamos softwares corporativos sob uma única bandeira social, isolando apenas os mercados de consumidor final.


## AJUSTE DE REALIDADE: BRANDING E LIMITES DO GOOGLE - [2026-09-23]
- **O Problema do Domínio "Apollo":** O termo "Apollo" puro é inviável para registro (.com/.com.br). O ecossistema precisa de um sufixo/prefixo único a nível Enterprise (Ex: ApolloForge, ApolloStack, ApolloSaaS) para viabilizar registros e buscas no YouTube.
- **O Gargalo do Gmail (Verificação de SMS):** O limite de criação de contas Google no aparelho do Criador foi estourado.
- **Solução Arquitetural de E-mail (Cloudflare Email Routing):** É proibido tentar criar 5 Gmails novos para e-mail de contato. A infraestrutura DEVE usar o serviço de Email Routing gratuito do Cloudflare/Hostinger atrelado ao domínio comprado. Ex: emails enviados para suporte@apollo[nome].com serão redirecionados invisivelmente para a caixa de entrada do Gmail pessoal existente do Mestre.
- **Identidade Visual Unificada:** Todos os projetos usarão a mesma Logomarca/Identidade (Mudando apenas o ícone central ou a cor de destaque), consolidando a marca mãe no cérebro do cliente, mesmo com domínios separados.


## REVISÃO DE DIRETRIZ DE DOMÍNIOS - [2026-09-23]
- **Tática de Segurança e Custo:** O Mestre decidiu priorizar o registro dos domínios .com.br para todos os projetos. 
  - **Motivo:** O .com.br exige CPF/CNPJ, o que afasta 99% dos bots e squatters internacionais, garantindo disponibilidade de nomes e um custo menor fixo (R$ 40/ano).
- **Alerta de Risco (Mercado Internacional):** Foi levantado um alerta arquitetural. Se o projeto visar o mercado internacional (faturar em Dólar), usar EXCLUSIVAMENTE .com.br vai destruir o SEO fora do Brasil e causar atrito de conversão (gringos hesitam em passar cartão em domínios regionais).
- **Plano de Mitigação (O Compromisso):** 
  1. Registrar e validar a operação inteira em Português primeiro no .com.br.
  2. Quando for lançar o idioma Inglês (venda na gringa), adquirir os domínios internacionais disponíveis (seja .com, .ai, .io ou .app) e integrá-los no Next.js (Vercel).


## [2026-09-23] FECHAMENTO DA ARQUITETURA DE MARCA E LANÇAMENTO
- O Mestre validou o lançamento em 2 Fases:
  1. Fase Nacional (Atual): Lançamento focado no Brasil usando o domínio .com.br (barato, blindado contra squatters, perfeito para validação do MVP em Português).
  2. Fase Internacional (Futuro): Aquisição do domínio .com (ou extensões de tech .ai/.io) na virada de chave para a língua Inglesa e faturamento em Dólar.
- Com as fundações de branding, infraestrutura Serverless, marketing, precificação e operações resolvidas, o projeto volta o foco 100% para o código (Painel Vercel / Modal).


## NAMING & DOMAIN UPDATE - [2026-09-23]
- **Broadcaster:** O Mestre contornou o bloqueio de domínio adquirindo/focando no termo **Apollo Broadcaster** (com "er"), garantindo a disponibilidade.
- **Achadinhos (Tradução/Localização para a Gringa):** O termo "Achadinhos" é uma gíria estritamente brasileira (focada em afiliação Shopee/AliExpress). Para o mercado internacional (EUA/Europa), o projeto de afiliação e automação de produtos adotará a marca **Apollo Finds** (baseado na forte tendência gringa de "TikTok Finds" e "Amazon Finds").


## NAMING UPDATE (ACHADINHOS INTERNACIONAL) - [2026-09-23]
- O Mestre detectou que a handle @ApolloFinds no YouTube já pertence a um canal de armas americano.
- **Alternativas Levantadas para "Achadinhos" em Inglês:** 
  1. Apollo Great Finds (Tradução natural e de alta conversão).
  2. Apollo Picks (As escolhas/curadoria do Apollo - muito usado em SaaS e Afiliados).
  3. Apollo Deals (Foco em promoções/ofertas).
  4. Apollo Gems (Joias escondidas / achados raros).


## [2026-09-23] FECHAMENTO DE NAMING - ACHADINHOS
- O Mestre decretou o nome oficial para a expansão internacional do projeto Achadinhos: **Apollo Finders** (pollofinders).
- O nome é forte, único e denota ação (Os "Buscadores" do Apollo trabalhando para achar os melhores produtos).


## NAMING UPDATE (A MARCA GUARDA-CHUVA) - [2026-09-23]
- O Mestre revelou seu nome artístico: **Apollo La Plata**. E já possui o Gmail nativo disso.
- **Decisão Arquitetural:** O conceito de Marca Mãe (O "Meta" do ecossistema Apollo) será o próprio nome/persona do Criador: **Apollo La Plata** (ou Apollo La Plata Studios). 
- **Estrutura Final:** A empresa mãe "Apollo La Plata" é a dona e criadora dos produtos satélites (Apollo Edit, Apollo Finds, Apollo Broadcaster). O Gmail oficial de administração da holding é o do Apollo La Plata.
- **Pocket Director:** Por ser uma ferramenta de uso pessoal do Criador, foi decidido que não precisa de domínio ou CNPJ próprio por enquanto.


## [2026-09-23] O GRANDE PROPÓSITO E DIRETRIZES OPERACIONAIS FINAIS
- **O Propósito Mestre:** A construção do Ecossistema Apollo (SaaS) é o motor financeiro para financiar o retorno da carreira artística do Criador (Apollo La Plata). Ferramentas como o Broadcaster e o Edit serão, futuramente, usadas para a própria produção artística.
- **Correção Operacional (Cloudflare):** Os domínios atuais já estão sob gestão do Cloudflare (direcionados para a Vercel). O recurso de Email Routing só precisa ser ativado na mesma dashboard.
- **Alerta de Segurança (Contas Google):** Foi expressamente banido o uso de números de SMS temporários (Telegram/SMS-Activate) para a criação de contas Gmail. O Google exige re-verificações futuras; sem o número físico, a conta morre.
- **E-mail Corporativo Oficial:** O atendimento ao público B2B será EXCLUSIVAMENTE feito pelos domínios da empresa (contato@apolloedit.com.br) via Cloudflare Routing, mantendo o nível Enterprise sem necessidade de novas contas Google.


## [2026-09-23] TÁTICA AVANÇADA DE CRIAÇÃO E VERIFICAÇÃO (RMT / ALTGRID)
- **Infraestrutura do Mestre:** O Criador já utiliza o AltGrid com Proxies Residenciais Brasileiros para isolamento de impressões digitais, permitindo rodar contas simultâneas de forma indetectável.
- **Riscos de SMS Descartável:**
  - **Para Gmail (Proibido):** O Google frequentemente exige o SMS original para permitir a troca do número ou em caso de verificação surpresa. O uso de SMS temporário para a conta Mestre/YouTube causa perda permanente.
  - **Para Redes Sociais (Permitido com ressalvas):** TikTok/Instagram/Twitter podem aceitar SMS temporário no cadastro. A tática de sobrevivência exige que, imediatamente após o cadastro (protegido pelo proxy), o Criador adicione um **App de Autenticação (2FA - Google Authenticator)** e vincule o E-mail de Domínio (Cloudflare), removendo o número de telefone temporário das configurações na sequência.


## [2026-09-23] ENCERRAMENTO DA SESSÃO: POSTERGAÇÃO FINANCEIRA E LANÇAMENTO LEAN
- O Criador encerrou o expediente.
- **Decisão Financeira (Lean Startup):** Devido ao custo de R$ 400 para registrar todos os domínios de uma vez, a estratégia foi alterada. Os domínios paralelos (Finders, Broadcaster, AutoBlog) NÃO serão comprados agora. A prioridade financeira é zero (risco baixo de roubo de domínio regional).
- **Foco Único:** Todo o foco e recursos ficam no **Apollo Edit** atual. 
- **Sobre a Marca Mãe (Holding):** A decisão sobre o nome unificado (Apollo La Plata / Apollo Labs) fica suspensa por não ser prioridade técnica no momento.


## [2026-09-24] NOME CONFIRMADO FRENTE A CONCORRENTES (POLLO.AI)
- **Validação de Concorrência:** O site pollo.ai possui proposta e agregador similares.
- **Decisão do Mestre:** O nome **Apollo Edit** está 100% mantido. O nome Apollo é de uso universal.
- **Diferencial Competitivo:** A concorrência não possui o estilo de código, o workflow focado, e o material único do Criador. A meta é dominar o Brasil primeiro e depois exportar.


## [2026-09-24] ESTRATÉGIA DE 'DOGFOODING' E VALIDAÇÃO DE MVP
- O Mestre confirmou que a plataforma concorrente utiliza o **MiniMax H3**, validando nossa escolha de tecnologia.
- **Estratégia de MVP (Dogfooding):** A versão 1.0 do Apollo Edit será construída para atender primariamente as próprias necessidades da Holding (produção do Autoblog, RMT, Broadcaster, Achadinhos). O sistema "nasce" tendo o próprio Criador como seu cliente Principal.
- Após a estabilização interna, a plataforma será aberta ao público comercial no Brasil. A mentalidade é: "A exclusividade absoluta de um produto é monopólio; a concorrência prova a demanda."


## [2026-09-24] O NASCIMENTO DA HOLDING: V5 APOLLO (O "META" DO CRIADOR)
- **Momento Eureca:** O Criador encontrou a marca guarda-chuva perfeita e globalmente disponível: **V5 APOLLO** (ou v5apollo).
- **Disponibilidade Global:** Todos os domínios de alto nível (incluindo o disputadíssimo .com) e absolutamente todas as redes sociais (YouTube, TikTok, Twitter, Facebook, Pinterest) estão livres.
- **Resolução de Conflitos:** Isso resolve definitivamente o choque de nome com concorrentes como o Pollo.ai e cria uma identidade corporativa (A Holding) blindada, profissional e com sonoridade de Big Tech (remetendo à infraestrutura V5 existente do criador).


## [2026-09-24] PIVOT DA METÁFORA VISUAL (DE CARRO PARA ESPAÇONAVE)
- O Criador definiu um pivot genial de UX/Copywriting. Como o nome definitivo é **V5 APOLLO**, a metáfora do sistema deixará de ser "Corrida de Carros/Piloto/Gasolina" e passará a ser **Exploração Espacial/Foguete Apollo/Comandante**.
- **Novo Dicionário Visual:** "Acelerar" vira "Ignição"; "Combustível" vira "Rocket Fuel/Energia"; o painel vira o "Cockpit da Espaçonave".
- Isso consolida a identidade corporativa e casa 100% com o imaginário global do Programa Apollo.


## [2026-09-24] ARQUITETURA DE BANCO DE DADOS (FEDERAÇÃO / MICROSERVIÇOS)
- **Correção Arquitetural:** O Criador reiterou a diretriz de **Isolamento Estrito de Dados**. Não usaremos um Supabase monolítico.
- **Modelo Adotado (Identity Provider + Micro-DBs):**
  - Existirá **UM Banco de Dados Central (V5 Apollo Auth)**: Responsável exclusivamente por gerenciar logins, senhas e assinaturas (O Passaporte Global).
  - Existirão **Bancos de Dados Isolados (Apollo Edit, AutoBlog, etc.)**: Cada braço terá sua própria conta do Supabase separada. Eles não se misturam. Eles apenas confiam no token de autenticação gerado pelo Banco Central.
- **Vantagem:** Evita vazamento de dados entre aplicações, previne limites de armazenamento de uma única conta gratuita e mantém o código modular.

## [2026-09-24] A "MODAL FARM" E ESCALABILIDADE VERTICAL
- **Expansão da Infraestrutura:** O Criador adicionou a 12ª conta Modal (polloeditweb) ao Pool.
- **Estratégia de Cluster:** A meta é expandir para 20 contas no curto prazo, reservando no mínimo 10 contas exclusivamente para a Orquestração de Vídeo (O modal mais custoso).
- **Justificativa:** A demanda de vídeo do próprio Criador (dogfooding/Autoblog) já esgota o teto de contas individuais rapidamente. Quando o sistema abrir para o SaaS comercial (usuários do V5 Apollo), o Load Balancer (Roteador de Contas) será crítico para manter o custo da infraestrutura próximo a zero.

## [2026-09-24] HOMOLOGAÇÃO DE VÍDEO (MINIMAX H3)
- O Criador definiu o **MiniMax H3** como o motor definitivo para a geração em massa de vídeos.
- O pool massivo de contas (Modal Farm) servirá para orquestrar e diluir o custo e os limites de requisição da geração desses milhares de vídeos por dia, garantindo estabilidade tanto para a holding (Autoblog) quanto para os clientes do SaaS V5 Apollo.
