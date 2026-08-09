/**
 * autopilot_logic.js
 * Lgica do modo "Piloto Automtico" (Full AI Mode)
 */

function sendAutoPilotMessage() {
    const input = document.getElementById('autopilot-input');
    const text = input.value.trim();
    if (!text) return;

    // Adiciona mensagem do usurio
    appendAutoPilotMessage('user', text);
    input.value = '';

    // Simula processamento da IA
    setTimeout(() => {
        const cost = Math.floor(Math.random() * 50) + 10;
        appendAutoPilotMessage('ai', `Entendido! Analisei seu pedido e verifiquei as configuraes ao lado. 
        <br><br>
        Esta operao custar aproximadamente <strong>${cost} Litros de Combustvel</strong> e englobar as seguintes etapas:
        <ul style="margin-top:10px; padding-left:20px; color:#ddd;">
            <li>Busca de Informao / Construo do Roteiro</li>
            <li>Gerao de 15 B-Rolls (Misturando IA e Bancos)</li>
            <li>Gerao de Narrao TTS e Lip Sync (Se Ativado)</li>
            <li>Montagem Automtica na Timeline usando Templates selecionados</li>
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
        appendAutoPilotMessage('ai', `Iniciando produo massiva! <br><br>
        <em> Etapa 1/4: Escrevendo Roteiro...</em>`);
        
        setTimeout(() => {
            appendAutoPilotMessage('ai', `<em> Etapa 2/4: Gerando e minerando imagens...</em>`);
            
            setTimeout(() => {
                appendAutoPilotMessage('ai', `<em> Etapa 3/4: Criando udio e lip sync...</em>`);
                
                setTimeout(() => {
                    appendAutoPilotMessage('ai', ` <strong>PRODUO CONCLUDA!</strong><br><br>
                    O vdeo foi montado e j est salvo no seu Bagageiro e no seu canal. Voc pode conferir os ativos na rea de Transferncia ou exportar diretamente!
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
            ${isAi ? '<strong style="color:var(--btn-yellow); display:block; margin-bottom:5px;"> Copiloto Supremo</strong>' : ''}
            ${text}
        </div>
    `;
    history.insertAdjacentHTML('beforeend', msgHTML);
    history.scrollTop = history.scrollHeight;
}

function saveAutoPilotConfig() {
    alert("Perfil de Configurao Salvo na Memria! A IA utilizar essas regras nas prximas delegaes.");
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
