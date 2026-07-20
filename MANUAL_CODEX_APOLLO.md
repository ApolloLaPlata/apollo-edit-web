# DIRETRIZES DE REDESIGN UX/UI DO APOLLO EDIT WEB PARA O CODEX

Olá, Codex.
Você está sendo encarregado de fatiar e converter um layout visual do Photoshop para código web (React / HTML+CSS / Tailwind). O usuário vai te passar as imagens fatiadas e o layout final que ele mesmo montou no Photoshop. O seu papel é transformar isso em um código ultra-leve e otimizado.

**ATENÇÃO MÁXIMA:** 
NÃO tente reinventar a identidade visual. O seu foco é fidelidade absoluta à imagem do Photoshop que o usuário fornecer. Siga estritamente as regras conceituais abaixo para a nomeação de classes, estruturação de componentes e UX.

---

## 1. O CONCEITO DO PRODUTO (NÃO É UM EDITOR DE VÍDEO COMUM)

O Apollo Edit Web é um **Sistema de Automação de Produção Audiovisual** disfarçado sob a metáfora de um **Jogo de RPG Mobile / Tycoon de Gerenciamento**.
O usuário sente que está administrando uma base de operações ou pilotando um carro de corrida. O vídeo final é apenas o resultado da "corrida".

**Dicionário de Domínio (Use estes termos no código e na UI):**
*   **Piloto** = O usuário.
*   **Copiloto** = Agentes de IA (ex: Roteiristas, Narradores).
*   **Motor** = O workflow de ferramentas / pipeline de renderização.
*   **Combustível (Gasolina)** = Energia gasta para executar automações de mídia (ex: gerar áudio, processar imagem).
*   **Cristais** = Moeda premium para adquirir novos recursos.
*   **KM (Kilometragem)** = O "Level/XP" do jogador, que mostra o quanto ele já processou no motor.
*   **Oficina** = Timeline / Área técnica.
*   **Bagageiro** = Biblioteca de arquivos / Inventário.
*   **Corrida / Missão** = O processo de renderização e automação trabalhando.

---

## 2. REGRAS DE ARQUITETURA VISUAL E CSS

O usuário vai te passar um layout que tem forte influência de jogos como *Survivor.io*, *Archero* e *Hero Adventure*, mas focado em usabilidade de ferramentas.

**Paleta de Cores Base (CSS Variables a serem mantidas):**
```css
:root {
  --bg-dark: #0a0510;       /* Fundo principal profundo */
  --panel-bg: #140b2e;      /* Fundo de cards/oficina */
  --neon-purple: #8b5cf6;   /* Destaque principal, energia */
  --neon-cyan: #00f0ff;     /* Bordas brilhantes, status ativo */
  --neon-gold: #fbbf24;     /* Cristais, conquistas, missões concluídas */
  --danger-red: #e11d48;    /* Alertas, falta de gasolina */
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
}
```

**Estilo dos Componentes:**
*   **Cards & Botões:** Use cantos arredondados (`border-radius: 12px` ou `16px`), fundo translúcido (Glassmorphism sutil `backdrop-filter: blur(8px)`) e bordas sólidas coloridas (`border: 2px solid var(--neon-purple)`).
*   **Sombras (Glow):** O neon não vem de cores brilhantes chapadas, mas de `box-shadow` emitindo luz. Exemplo: `box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);`
*   **Hierarquia:** As informações devem ser GIGANTES e legíveis, igual a jogos mobile. Botões de ação principais devem ocupar a tela inteira se estiver no mobile.
*   **Responsividade:** O design é *Mobile First / Painel Vertical First*. Primeiro adapte tudo para caber numa tela estreita (estilo celular ou painel lateral), depois expanda para telas widescreen.

---

## 3. A NOVA HOME: "CENTRO DE COMANDO"

Quando for montar o código da Home (Hub), ela DEVE ter as seguintes seções estruturadas no código:

1.  **HUD do Piloto (Topo):** 
    *   Exibição do Avatar do Piloto.
    *   Barra de Gasolina ⛽
    *   Saldo de Cristais 💎
    *   Odômetro (KM rodados).
2.  **Missão Atual (Card Principal):**
    *   Barra de progresso de renderização/criação ("Vídeo sobre Bitcoin - 70%").
    *   Botões de Ação Imediata ("Acelerar com Nitro", "Ver Oficina").
3.  **NPC / Diretor de IA:**
    *   Uma área dedicada ao "Conselheiro" que fala com o usuário. Ex: *"Piloto, o áudio já terminou de processar. Podemos acelerar o motor de vídeo?"*
4.  **Bagageiro (Inventário Rápido):**
    *   Slots quadrados de RPG (estilo mochila) mostrando os últimos arquivos gerados.
5.  **Área de Ferramentas (Oficina):**
    *   Somente os botões primários organizados de forma não-poluída. (As 69 páginas originais foram ocultadas do usuário casual e estão apenas no Dev Mode do Antigravity).

---

## 4. O SEU FLUXO DE TRABALHO COM O USUÁRIO

1.  **Receba o Design:** O usuário te enviará imagens do Photoshop que ele mesmo fatiou e preparou.
2.  **Extraia e Isole:** Crie um `index.html` limpo.
3.  **Gere o CSS/Tailwind:** Escreva o código perfeitamente idêntico ao Photoshop. Não invente margens, copie as margens visuais da imagem.
4.  **Crie Interatividade Básica:** Adicione efeitos de `:hover` nos botões (aumentar levemente a sombra neon, efeito de botão sendo pressionado `transform: scale(0.98)`).
5.  **Entregue o Código Pronto para o Antigravity:** Quando terminar, avise o usuário que o HTML/CSS está pronto para ser passado para o *Antigravity* (o agente de backend), que fará as conexões pesadas das APIs e iFrames do Apollo OS.

Bom trabalho, Codex! Trate cada componente de interface como se estivesse fazendo a UI de um jogo Triplo-A.
