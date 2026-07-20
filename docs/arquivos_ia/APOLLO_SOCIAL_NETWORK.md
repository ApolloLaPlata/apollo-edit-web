# 🌐 Apollo Edit - Hub Social e Competição Pessoal

Este documento consolida todas as ideias focadas na rede social, prova de status e consistência técnica para garantir a identidade dos canais de cada usuário, assegurando que este conhecimento nunca se perca devido a limites de chat.

## 1. O Perfil Social (A Garagem Pública)
Diferente de editores frios (como Premiere ou CapCut), o Apollo possui perfis públicos de criadores. O Perfil de um "Piloto" atua como sua página de apresentação:
*   **Vitrine do Avatar:** Mostra em 3D ou 2D o "Carro" do jogador no nível máximo atual dele e as "Roupas" (Skins) do seu personagem.
*   **Sala de Troféus:** Exibe as conquistas (ex: *Lendário: Renderizou 1.000 horas de vídeos*).
*   **Gestão de Canais (Prova Social):** O usuário pode conectar ou linkar seus canais reais do YouTube ao perfil. Isso serve como vitrine. "Se esse cara tem um canal de 1 milhão de views usando este software, ele sabe o que faz."
*   **Loja Pessoal:** Se o usuário colocou Sistemas de Prompts, Clonagem RVC ou "Quadradinhos de API" à venda no Mercado P2P, os itens aparecerão no Perfil dele.

## 2. O Mural da Fama (Leaderboard / Ranking)
A gamificação impulsiona o uso da ferramenta por pura vaidade humana.
*   **O Placar de Quilometragem:** Cada renderização e tempo processado (O consumo do FFmpeg) adiciona "Kilometragem" ao Piloto.
*   **A Corrida Semanal:** Na aba principal do site, haverá um Ranking dos Pilotos que "Mais Correram" na semana e no mês. Ficar no Top 10 pode dar prêmios semanais (Cristais) e títulos exclusivos para o Perfil.
*   Isso força o usuário a produzir vídeos todos os dias para não cair no ranking, gerando engajamento diário e receita constante de anúncios ou venda de Cristais.

## 3. O Pipeline de Consistência (Solução RVC / Clonagem)
Sistemas genéricos sofrem com quebra de identidade. Se o usuário usa o TTS do Google num dia e o VoiceMaker no outro, o personagem dele perde a voz, estragando o canal do YouTube.
*   **O Problema Resolvido:** O Apollo adota um pipeline duplo para todas as vozes.
*   **Passo 1 (Geração Bruta):** O usuário pode gerar as vozes em qualquer API (inclusive as robóticas e gratuitas) apenas para pegar a métrica e o ritmo da fala.
*   **Passo 2 (Filtro Normalizador RVC):** Uma vez que o áudio bruto está na Área de Transferência, o usuário joga ele na "Fábrica de Dublagem" (Aba do RVC). O sistema aplica a Clonagem de Voz (Voice Cloning) baseada no personagem do canal. 
*   **Resultado:** Não importa qual foi a IA de origem da voz ou se a API era a mais vagabunda do mercado; ao passar pelo "Filtro RVC", o áudio final soará 100% como o narrador original do canal. A Identidade é protegida.

## 4. Classificação de Clonagem (Selo de Qualidade)
Para facilitar o workflow dos usuários leigos:
*   As vozes disponíveis no "Bagageiro" ou criadas nas abas terão tags visuais informando se a voz é **[Clonável]** ou **[Final]**. Isso instrui o usuário a saber se precisa passar a peça de áudio pela Aba do RVC antes de enviar para o renderizador final.

---
**Nota de Segurança Arquitetural:** Com a rede social e a economia totalmente definidas e escritas nestes documentos anexos, a equipe tem o "manual de instruções" completo do game. Se houver falha sistêmica, perda de conversas, reinícios ou migrações de LLM, **toda a lógica do produto está salva neste cérebro persistente**.
