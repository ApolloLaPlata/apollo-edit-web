/**
 * apollo_tour.js
 * Sistema de Onboarding para Primeiros Usuários (Tour Guiado)
 */

document.addEventListener('DOMContentLoaded', () => {
    // Roda o tour apenas na tela HUB e se for a primeira vez
    const isHub = window.location.pathname.includes('hub.html') || window.location.pathname === '/' || window.location.pathname === '';
    const hasSeenTour = localStorage.getItem('apollo_has_seen_tour');
    
    if (isHub && !hasSeenTour) {
        // Atrasa um pouco para dar tempo de carregar a UI
        setTimeout(startApolloTour, 1500);
    }
});

function startApolloTour() {
    // Bloqueia rolagem
    document.body.style.overflow = 'hidden';

    const style = document.createElement('style');
    style.innerHTML = `
        .tour-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.85);
            z-index: 100000;
            display: flex;
            justify-content: center;
            align-items: center;
            opacity: 0;
            transition: opacity 0.5s;
        }
        .tour-highlight {
            position: absolute;
            border: 3px dashed var(--btn-yellow, #facc15);
            box-shadow: 0 0 0 9999px rgba(0,0,0,0.85);
            border-radius: 8px;
            z-index: 100001;
            pointer-events: none;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .tour-dialog {
            position: absolute;
            background: #111;
            border: 2px solid var(--btn-purple, #8b5cf6);
            border-radius: 12px;
            padding: 20px;
            width: 350px;
            color: #fff;
            z-index: 100002;
            box-shadow: 0 10px 30px rgba(139, 92, 246, 0.5);
            text-align: center;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .tour-dialog h3 {
            font-family: 'Bangers', cursive;
            color: var(--btn-yellow);
            font-size: 1.8rem;
            margin-top: 0;
        }
    `;
    document.head.appendChild(style);

    const overlay = document.createElement('div');
    overlay.className = 'tour-overlay';
    
    const highlight = document.createElement('div');
    highlight.className = 'tour-highlight';

    const dialog = document.createElement('div');
    dialog.className = 'tour-dialog';
    dialog.innerHTML = `
        <h3 id="tour-title">BEM-VINDO AO APOLLO!</h3>
        <p id="tour-text">Preparado para revolucionar sua produção de vídeos?</p>
        <div style="display:flex; justify-content:space-between; margin-top:20px;">
            <button class="btn" style="background:#444; color:#fff;" onclick="endApolloTour()">Pular</button>
            <button class="btn yellow" id="tour-next-btn">PRÓXIMO 🚀</button>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(highlight);
    document.body.appendChild(dialog);

    // Fade in inicial
    setTimeout(() => { overlay.style.opacity = '1'; }, 50);

    const steps = [
        {
            title: "ECONOMIA & RECURSOS",
            text: "Aqui em cima você vê seus Cristais e Gasolina. Você gasta Gasolina para renderizar vídeos e ganha mais completando Missões!",
            targetSelector: ".user-widget", // Cabeçalho direito
            dialogOffset: { top: 70, left: -200 }
        },
        {
            title: "ÁREA DE TRANSFERÊNCIA",
            text: "Os Quadradinhos Mágicos! Arraste imagens, áudios e prompts para a área invisível no canto inferior direito. O sistema suga e envia para a IA.",
            targetSelector: "#hud-item-container", // Transfer Area HUD
            dialogOffset: { top: -250, left: -100 }
        },
        {
            title: "O SEU COPILOTO",
            text: "Não sabe o que fazer? Clique em mim! Eu sou sua IA Pessoal, acompanho tudo que você faz e te ajudo a apertar os botões certos.",
            targetSelector: "#copilot-mascot-btn", // Mascote
            dialogOffset: { top: -200, left: -300 }
        }
    ];

    let currentStep = -1;

    function nextStep() {
        if(window.playClickSound) playClickSound();
        currentStep++;

        if (currentStep >= steps.length) {
            endApolloTour();
            return;
        }

        const step = steps[currentStep];
        const target = document.querySelector(step.targetSelector);

        if (!target) {
            // Se o elemento não existir na tela atual, pula
            console.warn("Tour Element not found: " + step.targetSelector);
            nextStep();
            return;
        }

        const rect = target.getBoundingClientRect();
        
        // Move o highlight
        highlight.style.top = (rect.top - 10) + 'px';
        highlight.style.left = (rect.left - 10) + 'px';
        highlight.style.width = (rect.width + 20) + 'px';
        highlight.style.height = (rect.height + 20) + 'px';

        // Move o dialog
        dialog.style.top = (rect.top + step.dialogOffset.top) + 'px';
        dialog.style.left = (rect.left + step.dialogOffset.left) + 'px';

        // Atualiza texto
        document.getElementById('tour-title').innerText = step.title;
        document.getElementById('tour-text').innerText = step.text;

        if (currentStep === steps.length - 1) {
            document.getElementById('tour-next-btn').innerText = "VAMOS NESSA! 🎉";
        }
    }

    document.getElementById('tour-next-btn').onclick = nextStep;

    window.endApolloTour = function() {
        if(window.playSuccessSound) playSuccessSound();
        localStorage.setItem('apollo_has_seen_tour', 'true');
        document.body.style.overflow = '';
        overlay.remove();
        highlight.remove();
        dialog.remove();
    }

    // Inicia o primeiro passo (Centro da tela)
    dialog.style.top = '40%';
    dialog.style.left = '50%';
    dialog.style.transform = 'translate(-50%, -50%)';
    highlight.style.display = 'none'; // Esconde highlight no passo 0 (Boas vindas)

    document.getElementById('tour-next-btn').onclick = () => {
        dialog.style.transform = ''; // Tira o translate pro posicionamento fixo funfar
        highlight.style.display = 'block';
        nextStep();
    }
}
