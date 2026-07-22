/**
 * copilot_hud.js
 * Injeta o Mascote/Copiloto IA no canto inferior direito da tela.
 * Oferece uma janela "intermediária" de chat para conversas rápidas e ações sugeridas,
 * além de ser flutuante e arrastável pelo usuário.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Only inject in top window to avoid duplicate bubbles in iframes
    if (window.self !== window.top) return;
    
    // Evita injetar duas vezes
    if (document.getElementById('apollo-copilot-hud')) return;

    // 1. Estrutura HTML do Copiloto
    const copilotHTML = `
        <div id="apollo-copilot-hud" style="position: fixed; bottom: 30px; right: 30px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end;">
            
            <!-- Janela Intermediária de Chat (Oculta por padrão) -->
            <div id="copilot-chat-window" style="display: none; width: 350px; background: #fff; border: 4px solid #000; border-radius: 20px; box-shadow: 6px 6px 0px #000; margin-bottom: 25px; position: relative; overflow: visible; font-family: 'Nunito', sans-serif;">
                
                <!-- Tail pointing to the mascot -->
                <svg style="position: absolute; bottom: -24px; right: 30px; width: 40px; height: 30px; z-index: 10;" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <polygon points="0,0 100,0 100,100" fill="#fff" stroke="#000" stroke-width="8"/>
                </svg>

                <!-- Header Comic style -->
                <div id="copilot-drag-handle" style="background: #facc15; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; cursor: grab; border-bottom: 4px solid #000; border-radius: 16px 16px 0 0;">
                    <strong style="color: #000; font-family: 'Bangers'; font-size: 1.5rem; letter-spacing: 1px; text-transform: uppercase;">🤖 Copiloto IA</strong>
                    <button onclick="toggleCopilotChat()" style="background: #ef4444; border: 3px solid #000; color: white; cursor: pointer; font-size: 1rem; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: 2px 2px 0px #000; transition: transform 0.1s;" onmousedown="this.style.transform='translate(2px, 2px)'; this.style.boxShadow='0 0 0 #000';" onmouseup="this.style.transform=''; this.style.boxShadow='2px 2px 0px #000';">✖</button>
                </div>
                
                <!-- Histórico de Chat -->
                <div id="copilot-chat-history" style="height: 250px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; background: #fff;">
                    <div style="background: #f1f5f9; border: 2px solid #000; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 0 #000;">
                        <p style="color: #000; font-size: 0.95rem; font-weight: bold; margin-bottom: 8px;">Yaaay! 👏 Olá! Eu sou o seu Copiloto de Produção. Pronto pra gente criar umas loucuras hoje?</p>
                        <p style="color: #475569; font-size: 0.85rem;">Estou de olho na sua Área de Transferência. O que vamos criar hoje?</p>
                    </div>
                </div>

                <!-- Input e Ações Rápidas -->
                <div style="padding: 10px; background: #fff; border-top: 4px solid #000; border-radius: 0 0 16px 16px;">
                    <div id="copilot-quick-actions" style="display: flex; gap: 5px; overflow-x: auto; margin-bottom: 10px; padding-bottom: 5px;">
                        <button onclick="simulateAITask('Gerar Imagens de Cachorro')" style="background: #fff; color: #000; border: 2px solid #000; border-radius: 12px; padding: 5px 10px; font-size: 0.8rem; cursor: pointer; white-space: nowrap; font-weight: bold; box-shadow: 2px 2px 0 #000;">🐕 Imagens de Cachorro</button>
                        <button onclick="window.location.href='noticias_autopilot.html'" style="background: var(--btn-green); color: #000; border: 2px solid #000; border-radius: 12px; padding: 5px 10px; font-size: 0.8rem; cursor: pointer; white-space: nowrap; font-weight: bold; box-shadow: 2px 2px 0 #000;">✈️ Piloto Automático</button>
                    </div>
                    <div style="display: flex; gap: 5px;">
                        <input type="text" id="copilot-input" placeholder="Peça para a IA..." style="flex: 1; padding: 8px 12px; border-radius: 8px; border: 2px solid #000; background: #fff; color: #000; font-weight: bold;" onkeydown="if(event.key === 'Enter') sendCopilotMessage()" />
                        <button onclick="sendCopilotMessage()" style="background: var(--btn-purple, #8b5cf6); color: white; border: 2px solid #000; border-radius: 8px; padding: 0 15px; cursor: pointer; font-weight: bold; box-shadow: 2px 2px 0 #000;">Enviar</button>
                    </div>
                </div>
            </div>

            <!-- Balãozinho rápido de erro (Automático) -->
            <div id="copilot-quick-bubble" style="display: none; position: absolute; bottom: 85px; right: 0; background: #fff; border: 3px solid #000; border-radius: 15px; padding: 10px 15px; box-shadow: 4px 4px 0px #000; font-family: 'Bangers', cursive; font-size: 1.2rem; color: #000; white-space: nowrap; z-index: 10000; opacity: 0; transition: opacity 0.3s; transform-origin: bottom right;">
                Mensagem Rápida!
                <div style="position: absolute; bottom: -10px; right: 20px; width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-top: 10px solid #000;"></div>
                <div style="position: absolute; bottom: -6px; right: 20px; width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-top: 10px solid #fff;"></div>
            </div>

            <!-- Mascote Flutuante (Botão) -->
            <div id="copilot-mascot-btn" style="width: 100px; height: 100px; background: var(--btn-purple, #8b5cf6); border-radius: 50%; box-shadow: 0 5px 15px rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; font-size: 3.5rem; cursor: pointer; border: 4px solid #fff; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0 0 30px rgba(139,92,246,0.8)';" onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 5px 15px rgba(0,0,0,0.5)';">
                🤖
            </div>
            
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', copilotHTML);
    makeCopilotDraggable();
});

// Alterna a visibilidade da janela de chat intermediária
window.toggleCopilotChat = function() {
    const chatWindow = document.getElementById('copilot-chat-window');
    const mascotBtn = document.getElementById('copilot-mascot-btn');
    const bubble = document.getElementById('copilot-quick-bubble');
    
    if (chatWindow.style.display === 'none') {
        chatWindow.style.display = 'block';
        mascotBtn.style.transform = 'scale(0.9)';
        if (bubble) bubble.style.display = 'none'; // Esconde o balãozinho se abrir o chat
    } else {
        chatWindow.style.display = 'none';
        mascotBtn.style.transform = 'scale(1)';
    }
}

// Envia mensagem do usuário para o chat da IA
window.sendCopilotMessage = function() {
    const input = document.getElementById('copilot-input');
    const msg = input.value.trim();
    if (!msg) return;

    addChatMessage('user', msg);
    input.value = '';

    // Simula resposta da IA (Placeholder)
    setTimeout(() => {
        addChatMessage('ai', `Entendido! Estou processando a sua instrução: "${msg}". No futuro, isso ativará a tela de carregamento e moverá os itens gerados direto para a Área de Transferência.`);
    }, 1000);
}

// Simula uma tarefa de IA que resulta em itens na Área de Transferência
window.simulateAITask = function(taskName) {
    addChatMessage('user', `Me ajude com: ${taskName}`);
    setTimeout(() => {
        addChatMessage('ai', `Iniciando a tarefa: ${taskName}. Aguarde o processamento no servidor...`);
        
        // Simula carregamento
        setTimeout(() => {
            addChatMessage('ai', `Pronto! Finalizei o processamento de "${taskName}". Os arquivos foram enviados para a sua Área de Transferência.`);
            // Se a Área de Transferência estiver carregada, envia mock data
            if (typeof addToTransferArea === 'function') {
                addToTransferArea('image', 'Lote de Cachorros', 'IA Generativa', '');
            }
            
            // Renderiza um botão dinâmico no chat da IA
            appendActionToChat('Você quer animar essas imagens?', 'Animar Imagens', () => {
                alert('A IA irá levar as imagens para o estúdio de animação agora!');
            });
            
        }, 2000);
    }, 500);
}

function addChatMessage(role, text) {
    const history = document.getElementById('copilot-chat-history');
    const isAi = role === 'ai';
    
    const bg = isAi ? '#f1f5f9' : 'var(--btn-blue, #3b82f6)';
    const color = isAi ? '#000' : '#fff';
    const align = isAi ? 'align-self: flex-start;' : 'align-self: flex-end;';
    const border = 'border: 2px solid #000; box-shadow: 2px 2px 0 #000;';
    
    const msgHTML = `
        <div style="background: ${bg}; border-radius: 10px; padding: 10px; width: 85%; ${align} ${border}">
            <p style="color: ${color}; font-size: 0.95rem; font-weight: ${isAi ? 'bold' : 'normal'};">${text}</p>
        </div>
    `;
    history.insertAdjacentHTML('beforeend', msgHTML);
    history.scrollTop = history.scrollHeight;
}

function appendActionToChat(text, btnLabel, callbackFn) {
    const history = document.getElementById('copilot-chat-history');
    
    // Cria container
    const container = document.createElement('div');
    container.style = "background: #2a2a2a; border-radius: 10px; padding: 10px; width: 85%; align-self: flex-start; border-left: 4px solid var(--btn-yellow, #facc15);";
    
    // Adiciona texto
    const p = document.createElement('p');
    p.style = "color: #fff; font-size: 0.95rem; margin-bottom: 8px;";
    p.innerText = text;
    container.appendChild(p);
    
    // Adiciona botao
    const btn = document.createElement('button');
    btn.style = "background: var(--btn-green, #10b981); color: #fff; border: none; border-radius: 8px; padding: 5px 10px; cursor: pointer; font-weight: bold;";
    btn.innerText = `▶ ${btnLabel}`;
    btn.onclick = callbackFn;
    container.appendChild(btn);
    
    history.appendChild(container);
    history.scrollTop = history.scrollHeight;
}

// Lógica de Draggable para o Mascote e sua janela
function makeCopilotDraggable() {
    const copilotHUD = document.getElementById('apollo-copilot-hud');
    const handle = document.getElementById('copilot-drag-handle');
    const mascot = document.getElementById('copilot-mascot-btn');
    
    let isDragging = false;
    let didDrag = false;
    let startX, startY, initialRight, initialBottom;

    const onMouseDown = (e) => {
        if(e.target.tagName === 'BUTTON') return;
        isDragging = true;
        didDrag = false;
        startX = e.clientX;
        startY = e.clientY;
        
        const rect = copilotHUD.getBoundingClientRect();
        initialRight = window.innerWidth - rect.right;
        initialBottom = window.innerHeight - rect.bottom;
        
        document.body.style.userSelect = 'none';
        document.querySelectorAll('iframe').forEach(f => f.style.pointerEvents = 'none');
    };

    handle.addEventListener('mousedown', onMouseDown);
    mascot.addEventListener('mousedown', onMouseDown);

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        
        if (Math.abs(dx) > 3 || Math.abs(dy) > 3) didDrag = true;
        
        let newRight = initialRight - dx;
        let newBottom = initialBottom - dy;
        
        // Bounding constraints
        const maxRight = window.innerWidth - copilotHUD.offsetWidth;
        const maxBottom = window.innerHeight - copilotHUD.offsetHeight;
        
        // Allow a little bit of margin so it doesn't get completely stuck
        newRight = Math.max(0, Math.min(newRight, maxRight));
        newBottom = Math.max(0, Math.min(newBottom, maxBottom));
        
        copilotHUD.style.right = `${newRight}px`;
        copilotHUD.style.bottom = `${newBottom}px`;
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        document.body.style.userSelect = '';
        document.querySelectorAll('iframe').forEach(f => f.style.pointerEvents = 'auto');
    });
    
    mascot.onclick = (e) => {
        if (didDrag) return; // Prevent toggle if user dragged it
        window.toggleCopilotChat();
    };
}

// ==========================================
// MÓDULOS DE CONSCIÊNCIA DA IA (SENSORS)
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    if (window.self !== window.top) return;
    initCopilotSensors();
    injectCopilotCSS();
});

function injectCopilotCSS() {
    const style = document.createElement('style');
    style.innerHTML = `
        
        @keyframes copilotClap {
            0%, 100% { transform: scale(1) rotate(0deg); }
            25% { transform: scale(1.2) rotate(-15deg); }
            50% { transform: scale(1.2) rotate(15deg); }
            75% { transform: scale(1.2) rotate(-15deg); }
        }
        .copilot-clap {
            animation: copilotClap 0.6s ease-in-out;
            box-shadow: 0 0 20px var(--btn-yellow, #facc15) !important;
        }
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

    // 2. Interceptador de Botões e Cliques Errados
    let randomClickCount = 0;
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('button, .btn');
        
        // Verifica cliques no vazio (erros de navegacao)
        const clickable = e.target.closest('button, a, input, select, .btn, .rpg-item, .hud-item, .tool-card');
        if (!clickable) {
            randomClickCount++;
            if (randomClickCount >= 5) {
                randomClickCount = 0;
                window.showCopilotQuickBubble("Tá perdido, chefe? Clica no mascote pra pedir um mapa!");
            }
        } else {
            randomClickCount = 0;
        }

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
                        
                        window.showCopilotQuickBubble(`Opa, peraí! 🛑 Você esqueceu de preencher algo!`);
                    }
                }
            }
        }
    }, true); // Capturing phase
}

window.showCopilotQuickBubble = function(text, duration = 4000) {
    const bubble = document.getElementById('copilot-quick-bubble');
    if (!bubble) return;
    bubble.innerHTML = text + `<div style="position: absolute; bottom: -10px; right: 20px; width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-top: 10px solid #000;"></div><div style="position: absolute; bottom: -6px; right: 20px; width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-top: 10px solid #fff;"></div>`;
    bubble.style.display = 'block';
    // trigger reflow
    void bubble.offsetWidth;
    bubble.style.opacity = '1';
    bubble.style.transform = 'scale(1)';
    
    clearTimeout(bubble.timeout);
    bubble.timeout = setTimeout(() => {
        bubble.style.opacity = '0';
        bubble.style.transform = 'scale(0.8)';
        setTimeout(() => bubble.style.display = 'none', 300);
    }, duration);
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
window.sendCopilotMessage = async function() {
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

    // --- Motor Local de Intenções (NLP Mock) ---
    const lowerMsg = msg.toLowerCase();
    
    // Intenção: Navegação
    const isNavigation = /ir para|abrir|navegar|onde|como vou para|aba/i.test(lowerMsg);
    
    if (isNavigation) {
        if (/mapeamento|timeline/i.test(lowerMsg)) {
            setTimeout(() => {
                addChatMessage('ai', `Entendido! Apertos os cintos, estou redirecionando você para a <b>Aba de Mapeamento (Timeline)</b> agora mesmo! 🚀`);
                setTimeout(() => window.location.href = 'noticias_timeline.html', 2000);
            }, 1000);
            return;
        }
        if (/config|configura|ajuste/i.test(lowerMsg)) {
            setTimeout(() => {
                addChatMessage('ai', `Buscando configurações globais... Levando você para as Configurações do Apollo! ⚙️`);
                setTimeout(() => window.location.href = 'noticias_settings.html', 2000); // Exemplo futuro
            }, 1000);
            return;
        }
        if (/invent|transferencia|itens/i.test(lowerMsg)) {
            setTimeout(() => {
                addChatMessage('ai', `Você já tem a Área de Transferência bem ali no cantinho, mas vou abri-la para você! 🎒`);
                setTimeout(() => {
                    if (window.laplataInventory) {
                        const panel = document.getElementById('laplata-inventory-panel');
                        if (panel) panel.style.display = 'flex';
                    }
                }, 1500);
            }, 1000);
            return;
        }
        if (/imagem|imagens|gerar imagem/i.test(lowerMsg)) {
            setTimeout(() => {
                addChatMessage('ai', `Partiu Estúdio de Imagens! Vou abrir a aba do Caçador para você gerar suas artes. 🎨`);
                setTimeout(() => window.location.href = 'noticias_miner.html', 2000);
            }, 1000);
            return;
        }
        if (/hub|inicio|voltar/i.test(lowerMsg)) {
            setTimeout(() => {
                addChatMessage('ai', `Voltando para a Base (Hub Central)! 🛸`);
                setTimeout(() => window.location.href = 'hub.html', 2000);
            }, 1000);
            return;
        }
    }

    // --- Integração Real com Lightning AI (Conta 1) ---
    // Adiciona loading
    const history = document.getElementById('copilot-chat-history');
    const loadingId = 'loading-' + Date.now();
    const loadingHTML = `
        <div id="${loadingId}" style="background: #f1f5f9; border-radius: 10px; padding: 10px; width: 85%; align-self: flex-start; border: 2px solid #000; box-shadow: 2px 2px 0 #000;">
            <p style="color: #000; font-size: 0.95rem; font-weight: bold; margin: 0;">Digitando...</p>
        </div>
    `;
    history.insertAdjacentHTML('beforeend', loadingHTML);
    history.scrollTop = history.scrollHeight;

    try {
        const apiKey = "16338b74-3f36-4c89-84db-a8e00b099058/roxingo/apollo-maquinas-virtuais";
        
        // Contexto inteligente para a IA saber em qual aba o usuario esta
        const sysPrompt = "Você é o Copiloto IA do Apollo Studio. Você é sarcástico, direto e muito inteligente. O usuário está atualmente na aba: " + context.current_tab + ". Ajude-o com dúvidas sobre criação de vídeo, roteiros ou operação do sistema.";

        const response = await fetch('https://api.apolloedit.com/api/lightning_proxy", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${apiKey}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                model: "nvidia-nemotron-3-ultra-550b-a55b",
                messages: [
                    { role: "system", content: sysPrompt },
                    { role: "user", content: msg }
                ]
            })
        });

        // Remove loading
        document.getElementById(loadingId).remove();

        if(!response.ok) {
            addChatMessage('ai', `❌ Erro de Conexão na Lightning AI. Status: ${response.status}`);
            return;
        }

        const data = await response.json();
        
        if (data.error) {
            addChatMessage('ai', `⚠️ Erro da API: ${data.error.message || JSON.stringify(data.error)}`);
            return;
        }

        const aiText = data.choices[0].message.content;
        addChatMessage('ai', aiText);

    } catch (error) {
        document.getElementById(loadingId).remove();
        addChatMessage('ai', `💥 Crash no sistema local! Detalhe: ${error.message}`);
    }
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
