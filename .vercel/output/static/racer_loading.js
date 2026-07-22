// racer_loading.js
// Injeta a estrutura HTML do Racing Loading dinamicamente na página
document.addEventListener('DOMContentLoaded', () => {
    const overlayHTML = `
        <div id="global-racer-overlay">
            <div class="speed-lines"></div>
            
            <div class="racer-hud">
                <h1 class="racer-title" id="racer-title">Tuning em Andamento...</h1>
                <div class="racer-status-box">
                    <p class="racer-status-text" id="racer-status-text">Aquecendo motores...</p>
                    <div class="nitro-tank">
                        <div class="nitro-fill" id="racer-nitro-bar">
                            <div class="nitro-glow"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="track-container">
                <div class="track-grid"></div>
            </div>

            <div class="racer-car-wrapper">
                <div id="racer-layers-container" style="position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
                    <img src="assets/car_level1.png" class="racer-car-layer" id="racer-base-layer" alt="Chassi Base" style="position: absolute; width: 100%; filter: drop-shadow(0 15px 10px rgba(0,0,0,0.8));">
                    <img src="assets/car_level1.png" class="racer-car-layer" id="racer-paint-layer" alt="Pintura Overlay" style="position: absolute; width: 100%; opacity: 0; mix-blend-mode: color;">
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', overlayHTML);
});

// API Global para as outras páginas usarem
window.ApolloRacer = {
    overlay: null,
    titleEl: null,
    statusEl: null,
    barEl: null,

    _initElements() {
        if (!this.overlay) this.overlay = document.getElementById('global-racer-overlay');
        if (!this.titleEl) this.titleEl = document.getElementById('racer-title');
        if (!this.statusEl) this.statusEl = document.getElementById('racer-status-text');
        if (!this.barEl) this.barEl = document.getElementById('racer-nitro-bar');
    },

    start(title = "Missão em Andamento...", costTier = "basic") {
        this._initElements();
        if (this.titleEl) this.titleEl.innerText = title;
        if (this.statusEl) this.statusEl.innerText = "Conectando peças...";
        if (this.barEl) this.barEl.style.width = "5%";
        
        // Fase 23: Desvinculação do Custo. Carrega o Avatar Persistente.
        const savedAvatarData = localStorage.getItem('apollo_car_avatar');
        let parts = { chassi: 'enferrujado', pintura: 'desgastada' };
        if (savedAvatarData) {
            try { parts = JSON.parse(savedAvatarData); } catch(e){}
        }

        const baseLayer = document.getElementById('racer-base-layer');
        const paintLayer = document.getElementById('racer-paint-layer');

        // Renderiza o Loadout (Sprite Overlays)
        if (baseLayer && paintLayer) {
            if (parts.chassi === 'esportivo') {
                baseLayer.src = 'assets/car_level2.png'; paintLayer.src = 'assets/car_level2.png';
            } else if (parts.chassi === 'blindado') {
                baseLayer.src = 'assets/car_level3.png'; paintLayer.src = 'assets/car_level3.png';
            } else {
                baseLayer.src = 'assets/car_level1.png'; paintLayer.src = 'assets/car_level1.png';
            }

            paintLayer.style.opacity = '1';
            if (parts.pintura === 'neon') {
                paintLayer.style.filter = 'hue-rotate(270deg) saturate(300%) brightness(1.5)';
                paintLayer.style.mixBlendMode = 'color-dodge';
            } else if (parts.pintura === 'ouro') {
                paintLayer.style.filter = 'sepia(100%) saturate(500%) hue-rotate(10deg) brightness(1.2)';
                paintLayer.style.mixBlendMode = 'color';
            } else {
                paintLayer.style.filter = 'grayscale(80%) brightness(70%) sepia(20%)';
                paintLayer.style.mixBlendMode = 'multiply';
            }
        }

        // Cenário Dinâmico baseado no Custo da API (costTier)
        const trackGrid = document.querySelector('.track-grid');
        const speedLines = document.querySelector('.speed-lines');
        if (trackGrid && speedLines) {
            if (costTier === 'premium') {
                // Cenário Ultra Cyberpunk
                trackGrid.style.backgroundImage = 'linear-gradient(rgba(155, 89, 182, 0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(155, 89, 182, 0.4) 1px, transparent 1px)';
                speedLines.style.background = 'repeating-linear-gradient(90deg, transparent 0, transparent 20px, rgba(155, 89, 182, 0.2) 20px, rgba(155, 89, 182, 0.2) 40px)';
            } else if (costTier === 'medium') {
                // Cenário Intermediário (Amarelo)
                trackGrid.style.backgroundImage = 'linear-gradient(rgba(250, 204, 21, 0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(250, 204, 21, 0.4) 1px, transparent 1px)';
                speedLines.style.background = 'repeating-linear-gradient(90deg, transparent 0, transparent 20px, rgba(250, 204, 21, 0.1) 20px, rgba(250, 204, 21, 0.1) 40px)';
            } else {
                // Cenário Básico (Escuro / Verde lodo)
                trackGrid.style.backgroundImage = 'linear-gradient(rgba(100, 255, 218, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(100, 255, 218, 0.1) 1px, transparent 1px)';
                speedLines.style.background = 'repeating-linear-gradient(90deg, transparent 0, transparent 20px, rgba(255, 255, 255, 0.05) 20px, rgba(255, 255, 255, 0.05) 40px)';
            }
        }

        if (this.overlay) {
            this.overlay.style.display = 'flex';
            this.overlay.style.opacity = '1';
        }
    },

    update(statusText, progressPercent = null) {
        this._initElements();
        if (this.statusEl && statusText) {
            this.statusEl.innerText = statusText;
        }
        if (this.barEl && progressPercent !== null) {
            this.barEl.style.width = Math.min(Math.max(progressPercent, 5), 100) + '%';
        }
    },

    finish(callback = null) {
        this._initElements();
        if (this.statusEl) this.statusEl.innerText = "🏁 Missão Concluída! Cortando a linha de chegada...";
        if (this.barEl) this.barEl.style.width = "100%";
        
        setTimeout(() => {
            if (this.overlay) {
                this.overlay.style.opacity = '0';
                setTimeout(() => {
                    this.overlay.style.display = 'none';
                    if (callback) callback();
                }, 500); // fade out
            }
        }, 1500);
    }
};

// ==========================================
// FUNÇÃO DEMO APENAS PARA FASE DE DESENVOLVIMENTO
// ==========================================
window.demoRacingLoader = function(costTier = 'medium') {
    
    // Inicia a corrida
    window.ApolloRacer.start("🛠️ Montando o Vídeo...", costTier);
    
    setTimeout(() => window.ApolloRacer.update("Gerando Roteiro de IA...", 20), 1000);
    setTimeout(() => window.ApolloRacer.update("Acoplando Peças Visuais (Runware)...", 45), 2500);
    setTimeout(() => window.ApolloRacer.update("Abastecendo com FFmpeg...", 70), 4000);
    setTimeout(() => window.ApolloRacer.update("Acelerando Renderização Final...", 90), 5500);
    
    setTimeout(() => {
        window.ApolloRacer.finish(() => {
            alert("Vídeo entregue na sua Garagem!");
        });
    }, 7000);
};
