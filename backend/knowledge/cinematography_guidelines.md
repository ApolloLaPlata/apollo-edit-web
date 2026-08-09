# Apollo Cinematography & Video Editing Guidelines

Este documento serve como o "Cérebro de Edição" do Apollo. Todos os Agentes (Pocket Director, Master Chef) e Rotas de IA que gerarem cortes matemáticos ou prompts de vídeo/imagem devem seguir estas regras estritas de cinematografia para garantir que os vídeos não pareçam robóticos.

## 1. Ritmo e Retenção (Pacing)
- **A Regra dos 3-5 Segundos:** A atenção na internet moderna é extremamente volátil (nicho Shorts/Vlogs). Nenhum plano (B-Roll ou A-Roll longo) deve durar mais que 3 a 5 segundos sem uma alteração visual (um zoom in, um corte de câmera, ou a inserção de um B-Roll).
- **Sincronia Rítmica:** Os cortes matemáticos DEVEM acontecer nos finais de frases ou pausas de respiração da narração, nunca cortando no meio de uma palavra ativa.
- **Rampas de Velocidade:** Em tutoriais ou vídeos lentos, o ritmo é cadenciado. Em clipes de alta energia, o ritmo deve ter picos de 1 a 2 segundos por take. O nível de energia ("energy_level") define a duração do corte.

## 2. Tipos de Cortes (Transitions & Cuts)
O sistema deve abandonar o "Hard Cut" eterno e adotar cortes orgânicos e invisíveis:
- **J-Cut:** O áudio da próxima cena entra um pouco antes do vídeo mudar. (Cria antecipação orgânica).
- **L-Cut:** O áudio da cena anterior continua tocando brevemente por baixo do vídeo da próxima cena.
- **Whip Pan & Zoom Transitions:** Utilizados para mascarar transições em momentos de alta energia ("High Energy"). Nunca usar fades lentos para vídeos de estilo "Shorts".

## 3. Direção de Arte e Enquadramento (Shot Angles & Prompts)
Na geração dos Prompts Visuais (Flux / LTX / Wan), a Inteligência Artificial deve atuar como um Diretor de Fotografia real, especificando o enquadramento em vez de apenas descrever o objeto:
- **Wide Shot / Establishing Shot:** Usado no início de uma sequência para estabelecer o ambiente. (Ex: "Ultra wide cinematic shot of a futuristic city").
- **Medium Shot:** Usado para diálogos ou pessoas falando. O padrão visual de 80% do vídeo.
- **Close-up / Extreme Close-up:** Usado EXCLUSIVAMENTE para destacar emoções, tensão dramática ou detalhes importantes. A duração desse corte deve ser menor (1 a 2.5 segundos).
- **Movimento de Câmera (Camera Movement):** Prompts de VÍDEO (I2V/T2V) DEVEM conter direções espaciais: "slow pan left", "dolly in", "drone shot revolving", para evitar que a IA gere imagens estáticas piscando.

## 4. Identidade e Humor (Aesthethics)
- Um editor humano tem sua própria assinatura. O AI Director deve classificar o nicho do vídeo e ajustar o JSON da linha do tempo.
- **Nicho Vlog/Gameplay:** Cortes secos e rápidos, inserts de memes (quando ativado), J-Cuts frequentes para cortar "respiros".
- **Nicho Documentário/Cinematic:** Pacing lento, transições Crossfade, B-Rolls alongados, prompts fotorealistas.

## DIRETRIZ DE OUTPUT PARA A IA (O "CUT SHEET"):
Quando o Diretor gerar o JSON de estruturação do roteiro, ele não deve gerar apenas "palavras-chave". Ele deve gerar o mapeamento exato de decupagem contendo:
- `broll_prompt`: O prompt cinematográfico avançado (com iluminação e câmera).
- `duration_seconds`: O tempo matemático da cena.
- `camera_angle`: O enquadramento exigido.
- `transition`: O tipo de corte para entrar nesta cena.
