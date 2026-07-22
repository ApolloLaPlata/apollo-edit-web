/**
 * autopilot_logic.js
 * Lógica do modo "Piloto Automático" (Full AI Mode)
 */

function sendAutoPilotMessage() {
    const input = document.getElementById('autopilot-input');
    const text = input.value.trim();
    if (!text) return;

    // Adiciona mensagem do usuário
    appendAutoPilotMessage('user', text);
    input.value = '';

    // Simula processamento da IA
    setTimeout(() => {
        const cost = Math.floor(Math.random() * 50) + 10;
        appendAutoPilotMessage('ai', `Entendido! Analisei seu pedido e verifiquei as configurações ao lado. 
        <br><br>
        Esta operação custará aproximadamente <strong>${cost} Litros de Combustível</strong> e englobará as seguintes etapas:
        <ul style="margin-top:10px; padding-left:20px; color:#ddd;">
            <li>Busca de Informação / Construção do Roteiro</li>
            <li>Geração de 15 B-Rolls (Misturando IA e Bancos)</li>
            <li>Geração de Narração TTS e Lip Sync (Se Ativado)</li>
            <li>Montagem Automática na Timeline usando Templates selecionados</li>
        </ul>
        <br>
        <button onclick="startAutoPilotTask()" style="background:var(--btn-green, #10b981); color:#fff; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; cursor:pointer;">CONFIRMAR E INICIAR</button>
        <button onclick="appendAutoPilotMessage('user', 'Cancelar')" style="background:var(--btn-red, #ef4444); color:#fff; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; cursor:pointer; margin-left:10px;">CANCELAR</button>
        `);
    }, 1000);
}

function startAutoPilotTask() {
    appendAutoPilotMessage('user', 'CONFIRMAR E INICIAR');
    setTimeout(() => {
        appendAutoPilotMessage('ai', `Iniciando produção massiva! <br><br>
        <em>⏳ Etapa 1/4: Escrevendo Roteiro...</em>`);
        
        setTimeout(() => {
            appendAutoPilotMessage('ai', `<em>⏳ Etapa 2/4: Gerando e minerando imagens...</em>`);
            
            setTimeout(() => {
                appendAutoPilotMessage('ai', `<em>⏳ Etapa 3/4: Criando áudio e lip sync...</em>`);
                
                setTimeout(() => {
                    appendAutoPilotMessage('ai', `✅ <strong>PRODUÇÃO CONCLUÍDA!</strong><br><br>
                    O vídeo foi montado e já está salvo no seu Bagageiro e no seu canal. Você pode conferir os ativos na Área de Transferência ou exportar diretamente!
                    <br><br>
                    <button onclick="window.location.href='noticias.html'" style="margin-top:10px; background:var(--btn-blue); color:#fff; border:none; padding:10px 20px; border-radius:8px; font-weight:bold; cursor:pointer;">Ir para o HUB</button>
                    `);
                }, 2000);
            }, 2000);
        }, 2000);
    }, 500);
}

function appendAutoPilotMessage(role, text) {
    const history = document.getElementById('main-chat-history');
    const isAi = role === 'ai';
    
    const msgHTML = `
        <div class="msg-${role}">
            ${isAi ? '<strong style="color:var(--btn-yellow); display:block; margin-bottom:5px;">🤖 Copiloto Supremo</strong>' : ''}
            ${text}
        </div>
    `;
    history.insertAdjacentHTML('beforeend', msgHTML);
    history.scrollTop = history.scrollHeight;
}

function saveAutoPilotConfig() {
    alert("Perfil de Configuração Salvo na Memória! A IA utilizará essas regras nas próximas delegações.");
}

// Suporte para tecla Enter no input
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById('autopilot-input');
    if (input) {
        input.addEventListener("keypress", (e) => {
            if (e.key === 'Enter') sendAutoPilotMessage();
        });
    }
});
