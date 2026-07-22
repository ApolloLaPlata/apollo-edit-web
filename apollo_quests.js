/**
 * apollo_quests.js
 * Injeta a aba de Missões (Quests) e gerencia recompensas.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Only inject if not already injected
    if (!document.getElementById('apollo-quest-overlay')) {
        injectQuestsSystem();
    }
});

function injectQuestsSystem() {
    const style = document.createElement('style');
    style.innerHTML = `
        .quest-panel-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(8px);
            z-index: 10001;
            display: none;
            justify-content: center;
            align-items: center;
        }
        .quest-panel {
            background: #0f172a;
            border: 2px solid var(--btn-purple, #8b5cf6);
            border-radius: 16px;
            width: 550px;
            max-width: 90%;
            box-shadow: 0 0 50px rgba(139, 92, 246, 0.4);
            padding: 30px;
            position: relative;
            color: #fff;
            font-family: 'Inter', sans-serif;
        }
        .quest-item {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .quest-info h4 {
            margin: 0 0 5px 0;
            color: var(--btn-yellow, #facc15);
            font-size: 1.1rem;
        }
        .quest-info p {
            margin: 0;
            font-size: 0.9rem;
            color: #94a3b8;
        }
        .quest-progress-bg {
            background: #0f172a;
            height: 12px;
            border-radius: 6px;
            margin-top: 10px;
            overflow: hidden;
            width: 100%;
            border: 1px solid #334155;
        }
        .quest-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #8b5cf6, #d946ef);
            width: 0%;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .btn-claim {
            background: #334155;
            color: #94a3b8;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: bold;
            cursor: not-allowed;
            transition: all 0.2s;
        }
        .btn-claim.ready {
            background: linear-gradient(45deg, #10b981, #059669);
            color: #fff;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
            transform: scale(1.05);
        }
        .btn-claim.ready:hover {
            transform: scale(1.1);
        }
        .quest-trigger-btn {
            position: fixed;
            bottom: 20px;
            right: 140px; /* Ao lado do copilot/inventario */
            background: linear-gradient(45deg, #8b5cf6, #3b0764);
            border: 2px solid #fff;
            color: #fff;
            padding: 12px 25px;
            border-radius: 30px;
            font-family: 'Bangers', cursive;
            font-size: 1.2rem;
            cursor: pointer;
            z-index: 9000;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            transition: transform 0.2s;
        }
        .quest-trigger-btn:hover {
            transform: scale(1.05);
        }
    `;
    document.head.appendChild(style);

    // Botão flutuante na tela removido (agora está na sidebar)

    // Estrutura do Modal
    const overlay = document.createElement('div');
    overlay.id = 'apollo-quest-overlay';
    overlay.className = 'quest-panel-overlay';
    overlay.innerHTML = `
        <div class="quest-panel">
            <button onclick="document.getElementById('apollo-quest-overlay').style.display='none'" style="position:absolute; top:20px; right:20px; background:none; border:none; color:#94a3b8; font-size:1.5rem; cursor:pointer;">✖</button>
            <h2 style="font-family:'Bangers', cursive; font-size:2.5rem; text-align:center; color:#fff; margin-top:0; letter-spacing: 2px;">🏆 MISSÕES DIÁRIAS</h2>
            
            <div id="quest-list">
                <!-- Injetado dinamicamente via JS -->
            </div>
            
        </div>
    `;
    document.body.appendChild(overlay);
}

// Lógica Real
window.apolloQuests = {
    state: {
        images_generated: 0,
        batches_completed: 0,
        freecut_exports: 0,
        claimed: {
            q1: false,
            q2: false,
            q3: false
        }
    },
    
    loadState: function() {
        const stored = localStorage.getItem('laplata_quests_state');
        // Zera diariamente se quiséssemos, mas no prototype vamos manter persistente
        if (stored) {
            this.state = { ...this.state, ...JSON.parse(stored) };
        }
    },
    
    saveState: function() {
        localStorage.setItem('laplata_quests_state', JSON.stringify(this.state));
        this.render(); // Update UI se aberto
    },

    addProgress: function(type, amount=1) {
        this.loadState();
        if (type === 'image') this.state.images_generated += amount;
        if (type === 'batch') this.state.batches_completed += amount;
        if (type === 'freecut_export') this.state.freecut_exports += amount;
        this.saveState();
        
        // Notifica se concluiu algo
        this.checkCompletions();
    },

    checkCompletions: function() {
        if (this.state.images_generated >= 5 && !this.state.claimed.q1) {
            if (window.apolloNotifications) window.apolloNotifications.add("Quest Completa!", "Produtor de Imagens. Vá na aba Missões para resgatar.", "success");
            if (window.apolloSFX) window.apolloSFX.play('success');
        }
        if (this.state.batches_completed >= 1 && !this.state.claimed.q2) {
            if (window.apolloNotifications) window.apolloNotifications.add("Quest Completa!", "Lote Assíncrono. Vá na aba Missões para resgatar.", "success");
            if (window.apolloSFX) window.apolloSFX.play('success');
        }
        if (this.state.freecut_exports >= 1 && !this.state.claimed.q3) {
            if (window.apolloNotifications) window.apolloNotifications.add("Quest Completa!", "Corte Rápido. Vá na aba Missões para resgatar.", "success");
            if (window.apolloSFX) window.apolloSFX.play('success');
        }
    },

    claim: async function(questId) {
        if (this.state.claimed[questId]) return;
        
        const db = await window.laplataDB.openDB();

        if (questId === 'q1' && this.state.images_generated >= 5) {
            await window.laplataDB.updateCurrency(db, 'cristais', 1); // Dá 1 Cristal
            this.state.claimed.q1 = true;
            this.saveState();
            if (window.apolloSFX) window.apolloSFX.play('success');
            alert("Resgatado 1 Cristal! 💎");
        }
        else if (questId === 'q2' && this.state.batches_completed >= 1) {
            await window.laplataDB.updateCurrency(db, 'gasolina', 20); // Dá 20 Gasolina
            this.state.claimed.q2 = true;
            this.saveState();
            if (window.apolloSFX) window.apolloSFX.play('success');
            alert("Resgatado 20 Gasolina! ⛽");
        }
        else if (questId === 'q3' && this.state.freecut_exports >= 1) {
            await window.laplataDB.updateCurrency(db, 'gasolina', 10); // Dá 10 Gasolina
            this.state.claimed.q3 = true;
            this.saveState();
            if (window.apolloSFX) window.apolloSFX.play('success');
            alert("Resgatado 10 Gasolina! ⛽");
        }
        
        // Atualiza a UI Global se estiver na tela
        window.laplataDB.updateTopNav(db);
        this.render();
    },

    render: function() {
        const list = document.getElementById('quest-list');
        if (!list) return;

        this.loadState();
        
        // Setup Q1
        const q1Max = 5;
        const q1Prog = Math.min(this.state.images_generated, q1Max);
        const q1Pct = (q1Prog / q1Max) * 100;
        const q1Ready = q1Prog === q1Max && !this.state.claimed.q1;
        
        // Setup Q2
        const q2Max = 1;
        const q2Prog = Math.min(this.state.batches_completed, q2Max);
        const q2Pct = (q2Prog / q2Max) * 100;
        const q2Ready = q2Prog === q2Max && !this.state.claimed.q2;

        // Setup Q3
        const q3Max = 1;
        const q3Prog = Math.min(this.state.freecut_exports, q3Max);
        const q3Pct = (q3Prog / q3Max) * 100;
        const q3Ready = q3Prog === q3Max && !this.state.claimed.q3;

        list.innerHTML = `
            <!-- Missão 1 -->
            <div class="quest-item">
                <div class="quest-info" style="flex:1; margin-right:15px;">
                    <h4>O Artista Digital</h4>
                    <p>Gere 5 imagens no Laboratório ou Thumbnail Studio.</p>
                    <div class="quest-progress-bg">
                        <div class="quest-progress-bar" style="width: ${q1Pct}%;"></div>
                    </div>
                    <small style="color:#888;">${q1Prog}/${q1Max}</small>
                </div>
                <div>
                    <button class="btn-claim ${q1Ready ? 'ready' : ''}" 
                            ${q1Ready ? \`onclick="window.apolloQuests.claim('q1')"\` : ''}>
                        ${this.state.claimed.q1 ? 'RESGATADO' : '1 💎'}
                    </button>
                </div>
            </div>

            <!-- Missão 2 -->
            <div class="quest-item">
                <div class="quest-info" style="flex:1; margin-right:15px;">
                    <h4>O Diretor de Massa</h4>
                    <p>Complete 1 Lote Inteiro no Job Runner.</p>
                    <div class="quest-progress-bg">
                        <div class="quest-progress-bar" style="width: ${q2Pct}%;"></div>
                    </div>
                    <small style="color:#888;">${q2Prog}/${q2Max}</small>
                </div>
                <div>
                    <button class="btn-claim ${q2Ready ? 'ready' : ''}" 
                            ${q2Ready ? \`onclick="window.apolloQuests.claim('q2')"\` : ''}>
                        ${this.state.claimed.q2 ? 'RESGATADO' : '20 ⛽'}
                    </button>
                </div>
            </div>

            <!-- Missão 3 -->
            <div class="quest-item">
                <div class="quest-info" style="flex:1; margin-right:15px;">
                    <h4>Corte Rápido</h4>
                    <p>Faça a exportação de 1 vídeo no FreeCut.</p>
                    <div class="quest-progress-bg">
                        <div class="quest-progress-bar" style="width: ${q3Pct}%;"></div>
                    </div>
                    <small style="color:#888;">${q3Prog}/${q3Max}</small>
                </div>
                <div>
                    <button class="btn-claim ${q3Ready ? 'ready' : ''}" 
                            ${q3Ready ? \`onclick="window.apolloQuests.claim('q3')"\` : ''}>
                        ${this.state.claimed.q3 ? 'RESGATADO' : '10 ⛽'}
                    </button>
                </div>
            </div>
        `;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.apolloQuests.loadState();
});
