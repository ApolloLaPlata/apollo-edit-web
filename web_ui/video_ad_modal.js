// Lógica para o Rewarded Ad (Assistir para ganhar Gasolina)
class RewardedAdSystem {
    constructor() {
        this.createModal();
    }

    createModal() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'ad-modal-overlay';
        this.overlay.style.display = 'none';

        this.modal = document.createElement('div');
        this.modal.className = 'ad-modal-content';

        this.videoPlaceholder = document.createElement('div');
        this.videoPlaceholder.className = 'ad-video-mock';
        this.videoPlaceholder.innerHTML = '<h2>🎬 PUBLICIDADE</h2><p>Aguarde o vídeo terminar para receber sua Gasolina.</p><div class="ad-spinner"></div>';

        this.timerDisplay = document.createElement('div');
        this.timerDisplay.className = 'ad-timer';
        this.timerDisplay.innerText = 'O vídeo começará em breve...';

        this.closeBtn = document.createElement('button');
        this.closeBtn.className = 'btn outline danger ad-close-btn';
        this.closeBtn.innerText = '✖ Fechar';
        this.closeBtn.style.display = 'none';
        
        this.closeBtn.addEventListener('click', () => this.close());

        this.modal.appendChild(this.videoPlaceholder);
        this.modal.appendChild(this.timerDisplay);
        this.modal.appendChild(this.closeBtn);
        this.overlay.appendChild(this.modal);
        document.body.appendChild(this.overlay);

        this.injectStyles();
    }

    injectStyles() {
        const style = document.createElement('style');
        style.innerHTML = `
            .ad-modal-overlay {
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0, 0, 0, 0.95);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
            }
            .ad-modal-content {
                width: 90%;
                max-width: 800px;
                height: 80%;
                background: #111;
                border: 2px solid #FFD32A;
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                position: relative;
                box-shadow: 0 0 50px rgba(255, 211, 42, 0.3);
            }
            .ad-video-mock {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #FFD32A;
                text-align: center;
            }
            .ad-spinner {
                width: 50px;
                height: 50px;
                border: 4px solid rgba(255, 211, 42, 0.3);
                border-top: 4px solid #FFD32A;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-top: 20px;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .ad-timer {
                padding: 20px;
                font-size: 24px;
                font-weight: bold;
                color: #fff;
                font-family: 'Bangers', cursive;
                letter-spacing: 2px;
            }
            .ad-close-btn {
                position: absolute;
                top: 20px;
                right: 20px;
            }
        `;
        document.head.appendChild(style);
    }

    show(rewardAmount = 10, callback) {
        this.overlay.style.display = 'flex';
        this.closeBtn.style.display = 'none';
        let timeLeft = 5; // Mock 5 seconds for testing instead of 30s
        
        this.timerDisplay.innerText = `Recompensa em ${timeLeft}s...`;
        this.timerDisplay.style.color = '#fff';

        const timerInterval = setInterval(() => {
            timeLeft--;
            if (timeLeft > 0) {
                this.timerDisplay.innerText = `Recompensa em ${timeLeft}s...`;
            } else {
                clearInterval(timerInterval);
                this.timerDisplay.innerText = `⛽ RECOMPENSA DE +${rewardAmount} L LIBERADA!`;
                this.timerDisplay.style.color = '#4CAF50';
                this.closeBtn.style.display = 'block';
                
                // Add reward to global state
                if (window.addGasolina) {
                    window.addGasolina(rewardAmount);
                } else {
                    console.log(`Gasolina added: ${rewardAmount}`);
                }

                if (callback) callback();
            }
        }, 1000);
    }

    close() {
        this.overlay.style.display = 'none';
    }
}

// Instantiate globally
window.adSystem = new RewardedAdSystem();
