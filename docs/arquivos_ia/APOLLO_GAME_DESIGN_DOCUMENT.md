
## 10. Bagageiro vs. Área de Transferência (Gerenciamento de Mídias)
- A janela flutuante da Área de Transferência possuirá botões dedicados, incluindo um botão de **Upload** e um de acesso ao **Bagageiro**.
- **Fluxo de Upload:** Ao fazer o upload de um arquivo, ele cai diretamente na **Área de Transferência** (uso ativo).
- **O Bagageiro (Storage Temporário):** Tudo o que o usuário não for usar no momento, ele joga para o Bagageiro. O Bagageiro é temporário e os arquivos expiram/são deletados com o tempo.
- **Monetização no Bagageiro:** O usuário pode gastar Cristais para aumentar o tempo de duração dos arquivos no Bagageiro.

## 11. Packs de Efeitos e Ativos de Edição (HDs de Efeitos)
- A plataforma irá oferecer **Packs de Efeitos** (vídeos HD, efeitos sonoros) prontos, pré-configurados e fáceis de usar diretamente na Timeline Web e na aba Diretor.
- Existirão packs gratuitos, premium e pacotes grandes vendidos a preços acessíveis.
- **Armazenamento:** Esses pacotes massivos não pesam nos nossos servidores principais de forma permanente. Eles podem ter um esquema de upload automático para a sessão do usuário ou ser baixados e re-upados. O objetivo é pegar os Terabytes de efeitos que já possuímos, tratá-los para o formato do software, e deixá-los prontos para uso sem dor de cabeça para o cliente. Esses efeitos ficam guardados na aba de Bagageiro ou numa aba terceira dedicada a Efeitos.
---


## 6. Diferencial e Identidade Core (Automação + IA)
- **Não é um CapCut:** O Apollo Edit Web não é para edições finas e milimétricas. É focado em **edição em lote, em grande quantidade e altamente personalizada** (ou genérica, caso o usuário não queira configurar nada).
- O grande diferencial é misturar IA com automação pesada, cobrindo uma lacuna que editores normais não atendem. Ele permite que o usuário traga seus arquivos locais e os insira num funil automatizado.

## 7. A Dinâmica dos 'Quadradinhos Mágicos'
- A 'Área de Transferência' flutuante funciona como um inventário de janelas do Windows.
- Nela ficam os **Quadradinhos Mágicos**: objetos visuais que representam mídias (fotos, vídeos, áudios) ou pacotes de IA consumíveis (Lote do Nano Banana, ChatGPT, ElevenLabs, etc).
- **Interação:** O usuário pode clicar nesses quadradinhos, ver preview, escutar áudios (em um player flutuante), arrastar para as ferramentas, ou até selecionar múltiplos para dar play ao mesmo tempo.
- O visual deve ser **100% Gamificado**: caixinhas brilhando, se mexendo e encaixando com efeitos visuais e feedback, como em um videogame.

## 8. Elementos de RPG e Monetização
- O sistema possui equipamentos visuais para o avatar e carro (chapéus, sapatos, capôs, rodas).
- Além de puramente cosméticos, os equipamentos e itens da loja poderão prover **vantagens reais** no ecossistema (ex: itens que aceleram o processamento, furam filas de espera no servidor, etc). Isso abre uma forte linha de monetização.

## 9. O Copiloto IA (Guia de Contexto)
- Um chatbot/robozinho fica rodando na parte inferior da tela, lendo o histórico de ações do usuário.
- **Sugestões Ativas:** Se o usuário gera um áudio, a IA nota e sugere: 'Você gerou um áudio. Quer juntá-lo com um vídeo e fazer legendas?'. A IA entende a ordem lógica das ferramentas.
- **Terceirização (Delegação Completa):** O usuário pode fazer apenas o início do trabalho e, caso tenha recursos, gastar 'Combustível' para delegar o resto do processo à IA. A IA pega as imagens, preenche a aba do Diretor, monta a Timeline e finaliza o serviço. Se não quiser gastar, o usuário faz o serviço 'no braço', arrastando e configurando os quadradinhos.

---

# 🧠 APOLLO STUDIO - GAME DESIGN & ECONOMIA (MEMÓRIA CENTRAL)

Este documento guarda os conceitos estruturais definitivos sobre como a economia, a monetização e a gamificação do Apollo Studio funcionam. É o nosso norte para manter o projeto coerente.

## 1. O Conceito Central: "MMORPG de Produtividade"
O Apollo não é apenas um gerador de vídeos. É um Ecossistema Fechado (Walled Garden) onde os criadores geram valor (vídeos), mas também interagem com um mercado interno viciante. Pilotos montam carros, roteiristas são Copilotos, e tudo gira em torno do status de ter o melhor conteúdo e o avatar mais raro no "Mural da Fama".

## 2. A Micro-Economia (Moedas Oficiais)
O HUD global de recursos é dividido em três pilares:
- **⛽ Gasolina (Tempo Render):** O "stamina" bruto. Descontado puramente na hora de pedir para o servidor gerar o vídeo final no `diretor.html`. Não é gasto em testes visuais de perfil.
- **🪙 Apollo Coins:** A moeda virtual "soft" do jogo (grind). Ganhamos girando a Roleta Diária, cumprindo missões ou assistindo anúncios (`tutorial.js`). Usado para comprar itens básicos e pagar taxas no mercado P2P.
- **💎 Cristais:** A moeda "hard" (Premium/Dinheiro Real). Usada para comprar pacotes avançados, itens lendários ou Gacha premium.

## 3. O Carro Avatar & Identidade (Oficina)
- **Desvinculação do Custo:** A aparência do carro **NÃO** muda aleatoriamente dependendo da API que ele usa. O carro é a Identidade/Status do Jogador. Se ele tem uma "Roda de Ouro", ele dirige a Roda de Ouro até ele querer trocar.
- **Engine Visual Zero-Cost:** Na `oficina.html`, o carro funciona via **Sprite Overlays** (CSS Filters e PNGs transparentes empilhados). Testar peças e trocar a cor do carro é 100% instantâneo e não gasta 1 centavo de API de Imagem do Servidor. O loadout final é salvo no `localStorage('apollo_car_avatar')`.
- **Raridade de Itens:** O jogo possui itens Comuns, Raros, Épicos e Lendários. Isso gera urgência e exclusividade. 

## 4. Cenários Dinâmicos de Carregamento
- Como o carro do jogador agora é persistente (não muda sozinho), a forma de representar visualmente o Custo/Qualidade de uma geração de API é mudando o **Background**.
- O carro do usuário é reconstruído na `loading.html`. Se a geração atual for cara (Premium), o fundo vira uma pista mágica cyberpunk (Neon). Se for barata, vira um asfalto escuro básico. 

## 5. O Trade Hub e a Loja de Pacotes (Mercado Negro)
A base principal da liquidez do Apollo, localizada em `mercado.html`:
- **Loja Oficial Apollo:** A plataforma atua como o "banco central", vendendo "Fardos de Cotas" com desconto (ex: Pacote de 100 Imagens Nano Banana) para abater o preço avulso (na tora) da API. Também vende as Lootboxes Misteriosas (Gacha).
- **Mercado da Comunidade (P2P):** Um painel de leilão aberto. Jogadores vendem peças de carro, roupas, Copilotos (treinados com prompts próprios) ou **Cotas Pessoais de API** que não usam (ex: o cara gosta do Luma e vende suas cotas sobressalentes do Veil 3 para outro jogador por Cristais).

## 6. Motor de Retenção Diária
- **Roleta da Sorte Diária:** Gacha simulado localizado no `hub.html`. Obriga o jogador a entrar no site todo dia (mesmo que não vá fazer vídeos) para tentar ganhar peças de carro, minutos de render ou Cristais.
- **Micro-Tutoriais Globais:** O botão flutuante de `tutorial.js` está em todas as páginas, e sempre mostrará o YouTube Short com a dica certeira sobre como aquela página ajuda ele a lucrar.

## 7. A Mecânica Base: "Automação em Etapas" (vs Timeline Tradicional)
O diferencial do Apollo contra editores como CapCut é que o Apollo **não é construído em volta de uma Timeline manual onde você arrasta tudo**. Ele opera na mecânica de **"Direção Assistida"**:
- O usuário ("Piloto") pré-configura parâmetros frios e deixa a IA ("Co-Piloto") executar etapas em sequência de forma automática no background.
- A Timeline só entra no final (se necessário) para ajustes de um vídeo já quase pronto.
- A edição é transformada num processo dinâmico: o usuário "joga" os recursos e observa o carro (sistema) processando tudo no fundo.

## 8. A Gestão de Recursos Físicos (O Bagageiro e A Área de Transferência)
Como arquivos de vídeo são muito pesados e o storage em nuvem é caro, foi criada a mecânica do **Bagageiro** combinada com a **Área de Transferência Flutuante**:

### A. O Bagageiro (Nuvem Pessoal Temporária)
- É a "Garagem/Porta-Malas" onde ficam guardados os vídeos base, áudios gerados e efeitos que o usuário fez upload.
- **Mecânica Financeira:** O Bagageiro **deleta os itens automaticamente** após alguns dias para salvar espaço do servidor. Se o usuário quiser manter o arquivo por mais tempo, ele gasta **Cristais** (Moeda Premium).
- **Venda de Pacotes:** A loja do Apollo venderá *Pacotes de Efeitos* (VFX, Músicas). Ao comprar, eles ficam permanentemente no Bagageiro, disponíveis na nuvem sem o usuário precisar baixá-los para o PC local. O "Combustível" da edição é pegar esses itens do Bagageiro e colocar na mesa.

### B. A Área de Transferência (HUD Flutuante Global)
- Um painel flutuante que **sobrepõe todo o site**, não importa em qual aba o usuário esteja. Ele funciona como uma prancheta de ativos da edição atual.
- **Preview Universal Constante:** Todo elemento gerado ou adicionado (imagem, áudio, roteiro) ganha um botão de preview imediato dentro do próprio HUD. Gerou um áudio? Tem um botão de 'Play' do lado pra ouvir na hora.
- **Ressonância Visual (Drag & Drop Gamificado):** A prancheta interage inteligentemente com a aba de fundo. Se o usuário estiver na aba de "Áudio", todos os ativos de áudio na Área de Transferência começarão a **piscar/brilhar em verde**, mostrando que são os "combustíveis" corretos para aquele slot. Textos ou imagens ficarão escurecidos ou vermelhos. Isso torna o sistema idiot-proof: a pessoa só precisa arrastar o que tá brilhando para dentro do buraco que tá brilhando.
- O usuário tira itens do Bagageiro e dropa (arrasta) nessa prancheta.
- Se ele gerou um TTS na aba de Áudio, o áudio vai para a Prancheta. Ele então **clica e dropa para a aba do Diretor**.
- **Player Integrado:** Na parte inferior desse HUD Flutuante, o usuário consegue dar "Play" nos elementos (ouvir o áudio, ver o vídeo gerado) na hora, antes de jogar nos slots finais.

### C. Ativos Textuais e a Timeline Invisível
- O Bagageiro também aceita **Arquivos de Texto**. O usuário cria um bloco de texto na interface e cola o roteiro. O sistema codifica visualmente: *Borda Amarela* (Template), *Borda Verde* (TTS), *Borda Laranja* (Roteiro Base).
- **Timeline Invisível:** Diferente de editores tradicionais, a base da Área de Transferência exibe um mini-preview contínuo do que está sendo gerado em background. O usuário não monta a timeline, ele observa ela se montar sozinha enquanto dropa as peças nos slots.

### D. Créditos como Itens Físicos (Consumíveis Estilo RPG)
- **O Fim do Saldo Frio:** No Apollo, o usuário não tem apenas um saldo invisível de "50 créditos". Os pacotes de API comprados na Loja viram **Itens Consumíveis no Bagageiro** (como poções de HP/MP num jogo de RPG).
- **Mecânica de Uso:** O usuário quer gerar uma imagem? Ele puxa o "Quadradinho Mágico do Flux Schnell (Restam: 50)" da Área de Transferência e dropa no slot de geração. Se o prompt pede 5 imagens, o item é consumido, reduz para 45 cargas e volta para a Área de Transferência. Se zerar, ele some.
- **Itens Gratuitos (Free-to-Play):** O Apollo fornecerá "Quadradinhos de Magia Branca" ilimitados (APIs open-source gratuitas). O usuário não paga nada para usar, mas o resultado é mais simples, exigindo que ele seja bom na edição manual posterior para o vídeo ficar profissional.

### E. Hard Currency vs Soft Currency (Cristais vs Gasolina)
- **Gasolina/Combustível (Soft Currency):** A moeda base. Toda ação básica no servidor (como usar o FFmpeg para renderizar o vídeo final) consome um pouco de Gasolina. Todo usuário ganha uma cota mensal grátis (suficiente para 5 a 10 vídeos).
- **Cristais (Hard Currency):** Moeda premium, com valor de dinheiro real. Necessária para comprar itens raros, automação Full-Auto, ou pagar as "Taxas de Anúncio" no Mercado P2P.

### F. A Economia Free-to-Play e a Inflação de Distância (Ads)
- **Custo por Quilometragem:** A geração não tem um custo fixo. O custo do FFmpeg e processamento é calculado pela complexidade do vídeo (A "Distância da Corrida" em km). Vídeos mais longos ou com mais efeitos custam mais Gasolina.
- **Inflação Publicitária:** Se um vídeo básico custa 1 "Tanque" (1 Anúncio Assistido), um vídeo mais longo e pesado pode exigir que o usuário assista a 2 ou 3 vídeos publicitários para encher a Gasolina necessária. O trabalho braçal de "assistir propaganda" compensa financeiramente o custo alto de servidor gerado por ele. O sistema sempre lucra mais do que o usuário gasta.

### G. O Hub Social e a Gamificação Pessoal (Perfil Público)
O Apollo Edit não é um editor isolado, é uma rede social de criadores.
- **Perfil do Usuário (A Garagem Pública):** Cada usuário tem uma página pública onde ele exibe seus troféus, o visual atual do seu Carro/Avatar, suas Roupas (Skins), e os canais do YouTube que ele gerencia.
- **Vitrine do Mercado:** O perfil também funciona como uma vitrine para as coisas que ele está vendendo no Mercado P2P (Prompts, RVC clones).
- **Mural da Fama (Leaderboard):** Os usuários ganham "Pontos de Kilometragem" por cada vídeo renderizado. Existe um ranking global mostrando os "Pilotos" que mais correram. Isso estimula o ego e a competição, forçando o uso contínuo (e consequentemente, mais visualizações de anúncios ou compra de Cristais).

### G. Taxas de Mercado (Sink de Cristais)
- O Mercado P2P tem uma barreira contra spam. Se um usuário quiser vender um "Sistema de Prompts" ou "Cota de API" lá, ele deve pagar uma taxa de publicação usando **Cristais**. Isso tira Cristais de circulação (deflação) e dá extremo valor à moeda premium.

### H. O Taxímetro de Combustível (Transparência de Custos)
- Em toda aba, qualquer ação que exija renderização ou processamento exibe um **medidor visual em tempo real**. O usuário vê exatamente quanto Combustível/Cristal aquela configuração vai custar antes de dar o Play. Não há surpresas.

### I. A Rota de Fuga (Exportação Drive)
- Para evitar que o Bagageiro delete os itens expirados, além de pagar para mantê-los na nuvem do Apollo, o usuário pode **Exportar** os itens gerados diretamente para seu Google Drive/Nuvem Pessoal, mantendo o controle total sobre sua produção.

### J. O Fluxo de Saída da Geração
- Quando a IA (ou a API) termina de processar a geração, o novo vídeo ou imagem **surge magicamente como um novo bloquinho na Área de Transferência**. Ele não fica escondido numa pasta. Ele brota na mão do usuário, pronto para a próxima etapa de edição.

## IV. Gestão de Consistência e Roteamento de Múltiplas APIs

### A. O Tanque de Combustível Fragmentado (Mix de APIs)
- **O Problema:** Um roteiro exige 15 imagens, mas o usuário só tem 5 cargas de *Flux* e 10 cargas de *Nano Banana*. Se misturar cegamente, a consistência visual quebra.
- **A Solução Visual:** Ao jogar os "Quadradinhos Mágicos" num slot que exige 15 gerações, surge um **Tanque de Combustível Lateral** (ou uma mini-timeline vertical) com 15 segmentos.
- **Pintando a Timeline:** O usuário jogou 1 cristal Flux (5 cargas)? Os primeiros 5 segmentos ficam Azuis (Cor do Flux). Jogou 1 cristal Nano Banana (10 cargas)? Os outros 10 ficam Amarelos. 
- **Micro-Gerenciamento Arrastável:** O usuário pode clicar e arrastar as cores dentro desse Tanque. Ele pode definir: "Cena 1, 4 e 5 usam Azul (Flux pq tem mais ação), o resto usa Amarelo (Nano Banana pq é lip-sync)". O consumo é calculado e roteado em Python para as APIs corretas cena a cena.

### B. O Pipeline de Consistência de Áudio (A Solução RVC)
- **O Problema das Vozes:** Usar o TTS gratuito do Google para uma cena e o VoiceMaker para outra quebra a consistência do personagem (timbre diferente).
- **A Solução (Clonagem Normalizadora):** O sistema Apollo não exige que a API primária tenha a voz perfeita. Ele adota um fluxo de 2 etapas:
  1. **Geração Genérica:** Gera o áudio base em qualquer API que o usuário tenha saldo (mesmo as gratuitas e robóticas).
  2. **Dublagem RVC (Filtro de Voz):** O áudio genérico passa pela aba de Dublagem (RVC - Retrieval-based Voice Conversion) onde um "Filtro de Personagem" é aplicado, normalizando o timbre. Assim, não importa a API de origem, o resultado final terá sempre a mesma voz do personagem do canal.
- **Classificação:** O sistema indicará visualmente (ex: tags) quais vozes podem ser clonadas/filtradas e quais já estão prontas.

---
**Status Atual da Memória:** O nível avançado da economia (Mistura de Consumíveis) e a solução de Consistência via RVC foram solidificados. O Apollo é uma máquina cirúrgica disfarçada de videogame.

## Regra de Ouro do Fluxo de Arquivos
- **O Funil Obrigatório:** A Área de Transferência não é apenas um atalho, ela é o **Ponto Central de Passagem** de quase tudo no site. Na maioria dos casos, os itens (sejam mídias locais do usuário ou arquivos recém-gerados pela IA) DEVEM obrigatoriamente passar pela Área de Transferência antes de ir para o Bagageiro ou para as outras abas/ferramentas. Ela atua como a 'esteira de produção' principal da fábrica.

## 12. Cosméticos do Mascote IA (Skins e Expressões)
- **Skins do Copiloto:** O assistente flutuante não precisa ser apenas um 'robozinho genérico'. O usuário poderá adquirir (via economia do jogo) novas skins e identidades para a sua IA (ex: Robô, Piloto, Cientista, Dona Maria, etc).
- **Expressões Animadas:** O mascote reagirá de forma vívida aos acontecimentos da tela. Ele terá estados de humor dinâmicos como **Raiva** (se muitos erros acontecerem), **Felicidade/Palmas** (ao concluir tarefas), **Alerta** (ao identificar problemas nos quadradinhos mágicos) e **Susto**. Isso aprofunda imensamente o grau de gamificação da plataforma.
---


## 13. Loja de Personalidades de IA (Sistema de Copilotos Múltiplos)
- O sistema não terá apenas uma IA. Existirá um catálogo (ex: 10 robôs/personagens).
- **Modelo Freemium:** 3 personagens serão gratuitos (com personalidades básicas), enquanto os outros 7 serão exclusivos, comprados com Cristais ou dinheiro real.
- **Identidade e System Prompt:** Cada personagem comprado não muda apenas o visual (skin). Ele possui um *System Prompt* único no backend, o que altera completamente o seu **jeito de falar**, seu senso de humor, suas gírias e sua abordagem ao ensinar o usuário. É uma personalização profunda de UX que serve como forte produto de venda.
---


## 14. O 'Mascot Forge' (Criação de Copilotos Customizados) e Mercado UGC
- **Criação pelo Usuário (UGC):** Existirá uma aba premium (acessada através de Cristais) onde o usuário pode 'forjar' o seu próprio robô do zero.
- **Fluxo de Criação:** O usuário joga uma imagem de referência, escreve a personalidade (System Prompt) desejada, e a nossa IA gera o design base e as sprites de expressão (triste, raiva, alerta, palmas). O usuário aprova, compila, e o robô está pronto.
- **Mercado Comunitário (Marketplace):** Os copilotos criados pelos usuários (ex: mascote do Trump, personagem de anime, etc) poderão ser **vendidos para outros usuários** dentro da plataforma. Isso cria um ecossistema econômico sustentável onde a comunidade gera os próprios cosméticos e roda a economia do jogo.
---


## 15. Sistema de Missões (Quests) e Recompensas
- **Missões Diárias/Semanais:** O sistema incentiva o uso contínuo através de desafios (ex: 'Gere 3 vídeos hoje', 'Use a ferramenta X'). 
- **Recompensa:** Completar missões concede recursos vitais (ex: 10 Litros de Combustível, Cristais, ou XP).
- **Gamificação do Hábito:** Isso transforma o trabalho de edição em um loop de recompensa satisfatório.

## 16. Ranking Interno de Copilotos (Popularidade)
- Não haverá ranking competitivo de diretores (para manter a complexidade baixa e o foco no trabalho), mas haverá um **Ranking de Ferramentas/Copilotos**.
- O sistema exibirá quais são os Roteiristas/Mascotes mais usados e populares da plataforma no momento. Isso incentiva criadores de Mascotes (no Marketplace UGC) a fazerem copilotos de qualidade para subirem no Top 10.
---

