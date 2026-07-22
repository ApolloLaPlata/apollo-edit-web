// ==========================================
// MÓDULOS DE CONSCIÊNCIA DA IA (SENSORS)
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    initCopilotSensors();
    injectCopilotCSS();
});

function injectCopilotCSS() {
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes copilotJump {
            0%, 100% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-20px) scale(1.1); }
        }
        .copilot-jump {
            animation: copilotJump 0.5s ease-in-out;
        }
        .copilot-glow {
            box-shadow: 0 0 20px var(--btn-green, #10b981) !important;
        }
        .copilot-error-glow {
            box-shadow: 0 0 20px var(--btn-red, #ef4444) !important;
        }
    `;
    document.head.appendChild(style);
}

function initCopilotSensors() {
    // 1. Observer da Área de Transferência
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                // Apenas interage ocasionalmente para não ficar chato
                if (Math.random() > 0.5) return; 
                
                const addedNode = mutation.addedNodes[0];
                if (addedNode.nodeType === 1 && addedNode.classList.contains('hud-item')) {
                    triggerCopilotReaction('item_added', addedNode.getAttribute('data-type'));
                }
            }
        });
    });

    // Tenta anexar observer na Área de Transferência
    const tryAttachObserver = setInterval(() => {
        const hudContainer = document.getElementById('hud-item-container');
        if (hudContainer) {
            observer.observe(hudContainer, { childList: true });
            clearInterval(tryAttachObserver);
        }
    }, 1000);

    // 2. Interceptador de Botões (Fallback)
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('button, .btn');
        if (btn && btn.id !== 'copilot-mascot-btn' && !btn.closest('#apollo-copilot-hud')) {
            // Verifica se a tela tem inputs vazios ao tentar salvar/gerar
            if (btn.innerText.toLowerCase().includes('gerar') || btn.innerText.toLowerCase().includes('salvar')) {
                const emptyInputs = Array.from(document.querySelectorAll('input[type="text"], textarea')).filter(i => i.value.trim() === '' && i.id !== 'copilot-input' && i.style.display !== 'none');
                
                if (emptyInputs.length > 0) {
                    // Impede o clique em 30% das vezes só para simular o fallback carismático
                    if (Math.random() > 0.7) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const mascotBtn = document.getElementById('copilot-mascot-btn');
                        mascotBtn.classList.add('copilot-jump', 'copilot-error-glow');
                        setTimeout(() => mascotBtn.classList.remove('copilot-jump', 'copilot-error-glow'), 500);
                        
                        window.toggleCopilotChat();
                        addChatMessage('ai', `Opa, peraí! 🛑 Você clicou em <b>${btn.innerText}</b> mas esqueceu de preencher alguns campos na tela! Não quero que o sistema dê erro. Dá uma olhada lá e tenta de novo.`);
                    }
                }
            }
        }
    }, true); // Capturing phase
}

// Coleta todo o contexto da tela para enviar pro Backend (LLM)
window.getSystemContext = function() {
    // Aba ativa baseada no pathname
    const path = window.location.pathname;
    let currentTab = 'Hub';
    const match = path.match(/noticias_([a-zA-Z0-9_]+)\.html/);
    if (match) currentTab = match[1];

    // Lê a Área de Transferência
    const transferItems = [];
    document.querySelectorAll('#hud-item-container .hud-item').forEach(item => {
        const strong = item.querySelector('strong');
        if (strong) {
            transferItems.push(item.getAttribute('data-type') + ' (' + strong.innerText + ')');
        }
    });

    return {
        user_language: navigator.language,
        current_tab: currentTab,
        transfer_area: transferItems,
        url: window.location.href
    };
};

// Modifica a função de enviar mensagem para injetar o contexto real
const originalSendCopilotMessage = window.sendCopilotMessage;
window.sendCopilotMessage = function() {
    const input = document.getElementById('copilot-input');
    const msg = input.value.trim();
    if (!msg) return;

    addChatMessage('user', msg);
    input.value = '';

    const context = window.getSystemContext();
    console.log('[COPILOTO] Payload enviado ao servidor:', { message: msg, context: context });

    const mascotBtn = document.getElementById('copilot-mascot-btn');
    mascotBtn.classList.add('copilot-jump');
    setTimeout(() => mascotBtn.classList.remove('copilot-jump'), 500);

    setTimeout(() => {
        addChatMessage('ai', `Li a sua mensagem! Processarei isso sabendo que você está na aba <b>${context.current_tab.toUpperCase()}</b> e que você tem ${context.transfer_area.length} itens na Área de Transferência.`);
    }, 1500);
}

function triggerCopilotReaction(type, data) {
    const mascotBtn = document.getElementById('copilot-mascot-btn');
    mascotBtn.classList.add('copilot-jump', 'copilot-glow');
    setTimeout(() => mascotBtn.classList.remove('copilot-jump', 'copilot-glow'), 500);

    // Abre a aba se estiver fechada e joga uma dica
    const chatWindow = document.getElementById('copilot-chat-window');
    if (chatWindow.style.display === 'none') {
        window.toggleCopilotChat();
    }

    if (type === 'item_added') {
        addChatMessage('ai', `👀 Eu vi que você colocou um novo item do tipo <b>${data}</b> na Área de Transferência. Muito bem! Quer que eu conecte isso à próxima etapa pra você?`);
        appendActionToChat('Levar para a Timeline', 'Montar Vídeo', () => {
            alert('Enviando para a Timeline...');
        });
    }
}
