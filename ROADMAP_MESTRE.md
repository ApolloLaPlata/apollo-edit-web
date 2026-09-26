# ROADMAP MESTRE - APOLLO EDIT WEB
*Registrado durante a sessão de brainstorm arquitetural.*

## V1.0: O CapCut Mágico (O Motor)
- **Foco:** Geração rápida, sem fricção. O usuário digita a história, o sistema entrega o vídeo.
- **Pipeline de Vídeo:** Forte uso de Imagem -> Animação (Img2Vid) para baratear custo e manter consistência de personagem.
- **Distribuição:** Sistema de agendamento e postagem automatizada nas redes.
- **Modelo de Negócios:** Assinatura + Créditos.

## V2.0: O Showrunner AI (A Alma)
- **Foco:** Personalização profunda e gestão de franquia.
- **Banco de Elenco (Casting):** Cadastro de personagens com Imagem de Referência (FaceID/IP-Adapter) + Voz Clonada (TTS) + Personalidade (Prompt RAG).
- **Memória Episódica:** A IA lembra de todos os vídeos já postados no canal para não repetir assuntos e manter a lore (Bíblia do Canal).
- **Montagem:** Introdução de transições (crossfade, etc).

## V3.0: A Agência Autônoma (A Inteligência)
- **Foco:** Automação de marketing e complexidade de áudio/vídeo.
- **Trend Surfing:** O robô pesquisa ativamente tendências no YouTube/TikTok e gera conteúdo baseado em demanda.
- **Atuação Mista:** Sai o estilo "documentário" e entra o Lip-Sync (H3/Modelos avançados). Múltiplos personagens dialogando na mesma tela (Podcast Mode).
- **Empacotamento Completo:** Geração autônoma de Thumbnails (Estúdio de Capas), Títulos Clickbait e Descrição SEO.
- **Controle Granular:** O usuário pode mandar regerar apenas a Cena 3, edição humana e templates.

## V4.0: O Sistema Operacional de Mídia (A Ferramenta Pro)
- **Foco:** O Editor NLE gamificado e colaborativo.
- **A Garagem (Assets):** O usuário passa a acessar as 4 abas nativas (Imagem, Vídeo, Áudio, TTS) avulsas para gerar material bruto e guardar na sua Garagem.
- **Upload Externo:** Aceita vídeo real gravado pelo usuário para a IA editar junto com os gerados.
- **Agente Co-Editor:** Edição feita via Chat ("IA, troca a música da cena 2 pra algo mais triste").

## V5.0: A Metrópole e a Economia (O Metajogo)
- **Foco:** Gamificação profunda e retenção.
- **Economia Interna:** "Mercado Negro", ranking de usuários. O usuário ganha XP, sobe o nível da conta e compra "GPUs virtuais" e "Combustível" para deixar o custo de geração de vídeo dele mais barato.
- **O Balde (Utilitários):** As ferramentas secundárias (Extrair Áudio, Cortar Vídeo, Transcrição isolada) viram um pacote extra para o usuário usar de forma avulsa.

## V6.0: O Império Multimídia (A Teia)
- **Foco:** Domínio fora das redes sociais de vídeo.
- **Autoblog Integrado:** O canal do cara agora tem um site. Todo vídeo postado vira automaticamente um Artigo de Blog Otimizado para SEO, escrito pela IA, monetizando com AdSense no tráfego orgânico do Google.

## V7.0: A Onipresença (A Skynet)
- **Foco:** Transmissão contínua e acessibilidade total.
- **Broadcaster:** Geração de Live Infinita (24/7) automática no YouTube/Twitch usando os avatares da V2.
- **Pocket Diretor (Mobile):** App nativo no celular do cara.
- **WhatsApp Bot:** O Diretor (IA) manda mensagem no zap do usuário: "Chefe, seu vídeo das 18h rendeu 10k views. Já gerei o de amanhã baseado nessa métrica, aprova?". O usuário aprova com um "Sim" no WhatsApp e o vídeo vai pro ar.

## REGRAS ARQUITETURAIS (APROVADO PELO DIRETOR EM 2026-09-21)
1. **Frontend Desacoplado:** Todos os frontends (Autoblog, Landing Pages) migram para **Vercel**, conectados a **Cloud DBs (ex: Supabase/Neon)**. O Apollo Backend opera apenas como orquestrador de IA/Mídia no Hugging Face.
2. **Uso Estratégico de LLM:** Robôs não devem ser máquinas de gastar dinheiro. Processos em background (Patrulha) ficam restritos ao tier gratuito (Lightning AI) em polling espaçado, acionando o modelo pago (OpenRouter) apenas em geração direta e autorizada pelo usuário.
