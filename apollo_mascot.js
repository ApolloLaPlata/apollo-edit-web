/**
 * APOLLO MASCOT (Companion)
 * Gerencia a interface visual do Mascote, animações de sprite e controle de microfone.
 */

class ApolloMascot {
    constructor() {
        this.sprites = {
            idle: 'assets/ruby_mascot.png',
            listening: 'assets/ruby_mascot.png', // Pode ter um brilho
            thinking: 'assets/ruby_mascot.png',
            speaking: 'assets/ruby_mascot.png',
            happy: 'assets/ruby_mascot.png', // Futuras sprites
            sad: 'assets/ruby_mascot.png',
            angry: 'assets/ruby_mascot.png'
        };
        
        this.currentState = 'idle';
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;

        this.initUI();
        this.initAudio();
        this.bindEvents();
    }

    initUI() {
        const mascotHtml = `
            <div id="apollo-mascot-container" style="position: fixed; bottom: 30px; left: 30px; z-index: 10000; display: flex; flex-direction: column; align-items: center; gap: 10px; transition: all 0.3s; cursor: pointer;">
                
                <!-- Bolha de Diálogo (Speech Bubble) -->
                <div id="mascot-speech-bubble" style="display: none; background: rgba(0, 0, 0, 0.8); border: 2px solid var(--btn-purple); border-radius: 12px; padding: 12px 20px; color: #fff; font-weight: bold; max-width: 250px; text-align: center; box-shadow: 0 5px 15px rgba(167, 139, 250, 0.3); transform-origin: bottom center; animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);">
                    Olá, mestre!
                </div>

                <!-- Avatar -->
                <div id="mascot-avatar" style="width: 100px; height: 100px; border-radius: 50%; background-image: url('${this.sprites.idle}'); background-size: cover; background-position: center; border: 3px solid #ffd700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.4); transition: transform 0.2s, filter 0.2s;">
                </div>

                <!-- Microfone Feedback -->
                <div id="mascot-mic-status" style="background: rgba(0,0,0,0.6); padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold; color: #aaa; text-transform: uppercase;">
                    Segure [ESPAÇO]
                </div>

            </div>
            <style>
                @keyframes popIn {
                    0% { transform: scale(0.5); opacity: 0; }
                    100% { transform: scale(1); opacity: 1; }
                }
                @keyframes pulseGlow {
                    0% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); border-color: #ef4444; }
                    50% { box-shadow: 0 0 30px rgba(239, 68, 68, 1); border-color: #f87171; }
                    100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); border-color: #ef4444; }
                }
                .mascot-listening {
                    animation: pulseGlow 1s infinite;
                    transform: scale(1.05);
                }
                .mascot-thinking {
                    filter: hue-rotate(180deg) brightness(1.2);
                    transform: scale(0.95);
                }
                .mascot-speaking {
                    filter: brightness(1.3);
                    transform: scale(1.1);
                }
            </style>
        `;
        document.body.insertAdjacentHTML('beforeend', mascotHtml);

        this.avatarEl = document.getElementById('mascot-avatar');
        this.speechBubble = document.getElementById('mascot-speech-bubble');
        this.micStatus = document.getElementById('mascot-mic-status');

        // Clicar no mascote também abre opções
        this.avatarEl.addEventListener('click', () => this.openMascotMenu());    async initAudio() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);

            this.mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) this.audioChunks.push(e.data);
            };

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.audioChunks = [];
                this.processAudio(audioBlob);
            };
        } catch (err) {
            console.warn("Mascot: Permissão de microfone negada ou indisponível.", err);
            this.micStatus.innerText = "Sem Microfone";
            this.micStatus.style.color = "#ef4444";
        }
    }

    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && !e.repeat && this.isValidTarget(e.target)) {
                this.startListening();
            }
        });

        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space' && this.isValidTarget(e.target)) {
                this.stopListening();
            }
        });
    }

    isValidTarget(target) {
        // Ignora a barra de espaço se o usuário estiver digitando num input/textarea
        const tag = target.tagName.toLowerCase();
        return tag !== 'input' && tag !== 'textarea' && !target.isContentEditable;
    }

    startListening() {
        if (!this.mediaRecorder || this.isRecording) return;
        this.isRecording = true;
        this.audioChunks = [];
        this.mediaRecorder.start();
        
        this.setEmotion('listening');
        this.micStatus.innerText = "🎤 Escutando...";
        this.micStatus.style.color = "#ef4444";
        if(window.apolloSfx) window.apolloSfx.play('click'); // Bip
    }

    stopListening() {
        if (!this.mediaRecorder || !this.isRecording) return;
        this.isRecording = false;
        this.mediaRecorder.stop();
        
        this.setEmotion('thinking');
        this.micStatus.innerText = "🧠 Pensando...";
        this.micStatus.style.color = "#a78bfa";
    }

    async processAudio(blob) {
        this.setEmotion('thinking');
        this.micStatus.innerText = "🧠 Pensando...";
        this.micStatus.style.color = "#a78bfa";

        try {
            // Converte Blob para Base64
            const reader = new FileReader();
            reader.readAsDataURL(blob);
            reader.onloadend = async () => {
                const base64Audio = reader.result.split(',')[1];
                
                // Determina a velocidade (Gasolina Comum vs Nitro)
                const forgeEnabled = window.apolloMascotForge !== undefined;
                const nitroLevel = forgeEnabled ? document.getElementById('select-nitro-level').value : 'free';

                try {
                    // Envia o áudio gravado para o Lightning (Cérebro + Ouvido)
                    const response = await fetch('http://localhost:5005/api/mascot/interact', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            audio_base64: base64Audio,
                            nitro_level: nitroLevel,
                            system_prompt: forgeEnabled && window.apolloMascotForge.selectedAvatar 
                                            ? window.apolloMascotForge.selectedAvatar.prompt 
                                            : "Você é um assistente gentil."
                        })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.status === 'success') {
                            
                            // Cobra cristais dependendo do Nitro escolhido
                            if (nitroLevel === 'nitro' && window.ApolloEconomy) {
                                window.ApolloEconomy.updateBalance('cristais', -2); // Exemplo: 2 cristais
                                if(window.apolloNotifications) window.apolloNotifications.add("Nitro Usado", "-2 Cristais pela GPU T4.");
                            } else if (nitroLevel === 'nitro_master' && window.ApolloEconomy) {
                                window.ApolloEconomy.updateBalance('cristais', -5); // Exemplo: 5 cristais
                                if(window.apolloNotifications) window.apolloNotifications.add("Nitro Master Usado", "-5 Cristais pela GPU Ultra.");
                            }

                            console.log("Mascot Heard (Lightning STT):", data.transcription);
                            this.handleResponse(data.response, data.audio_response);
                            return;
                        }
                    }
                } catch (e) {
                    console.warn("Lightning Server offline. Usando Fallback.");
                }

                // Fallback offline
                setTimeout(() => {
                    const mockResponse = {
                        text: "Servidor Lightning offline. Mas o estúdio multimídia está pronto!",
                        emotion: "sad",
                        action: { type: "navigate", payload: { file: "estudio_multimidia.html", title: "Estúdio" } }
                    };
                    this.handleResponse(mockResponse, null);
                }, 1000);
            };
        } catch (err) {
            console.error("Erro ao processar áudio:", err);
            this.setEmotion('idle');
        }
    }

    handleResponse(res, audioBase64) {
        this.setEmotion(res.emotion);
        
        if (audioBase64 && audioBase64 !== "audio_base64_simulado_aqui") {
            this.speechBubble.innerText = res.text;
            this.speechBubble.style.display = 'block';
            const audio = new Audio("data:audio/wav;base64," + audioBase64);
            audio.play();
            audio.onended = () => this.speechBubble.style.display = 'none';
        } else {
            this.speak(res.text); // Usa o TTS do navegador caso a API retorne null ou fallback
        }// Usa o TTS do navegador
        }
        
        if(res.action) {
            if(res.action.type === 'navigate') {
                if(window.parent && window.parent.openAppTab) {
                    window.parent.openAppTab(res.action.payload.file, res.action.payload.title, true);
                }
            } else if (res.action.type === 'bagageiro') {
                // Acessa a API nativa
                if(window.apolloTransferOS) window.apolloTransferOS.toggleFolder('bagageiro');
            }
        }

        // Restaura idle após 3s
        setTimeout(() => {
            this.setEmotion('idle');
            this.micStatus.innerText = "Segure [ESPAÇO]";
            this.micStatus.style.color = "#aaa";
        }, 4000);
    }

    setEmotion(emotion) {
        this.currentState = emotion;
        // Muda a sprite baseada na emoção
        this.avatarEl.style.backgroundImage = `url('${this.sprites[emotion] || this.sprites.idle}')`;
        
        // Remove classes antigas
        this.avatarEl.className = '';
        if(emotion === 'listening') this.avatarEl.classList.add('mascot-listening');
        if(emotion === 'thinking') this.avatarEl.classList.add('mascot-thinking');
        if(emotion === 'speaking') this.avatarEl.classList.add('mascot-speaking');
        
        // Cor do anel baseada na emoção
        let borderColor = '#ffd700'; // idle (yellow)
        if(emotion === 'listening') borderColor = '#ef4444'; // red
        if(emotion === 'thinking') borderColor = '#a78bfa'; // purple
        if(emotion === 'happy') borderColor = '#10b981'; // green
        if(emotion === 'sad') borderColor = '#3b82f6'; // blue
        this.avatarEl.style.borderColor = borderColor;
    }

    speak(text) {
        this.speechBubble.innerText = text;
        this.speechBubble.style.display = 'block';
        
        // TTS Nativo do navegador temporário (até plugar o ElevenLabs)
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'pt-BR';
        utterance.onend = () => {
            this.speechBubble.style.display = 'none';
        };
        window.speechSynthesis.speak(utterance);
    }

    openMascotMenu() {
        alert("Em breve: Mascot Forge! Aqui você poderá forjar um novo ajudante (Visual + Voz + Prompt), alterar para o modo 'Homem-Aranha' ou 'Master Chef'.");
    }
}

// Injeta globalmente quando carregado
document.addEventListener('DOMContentLoaded', () => {
    window.apolloCompanion = new ApolloMascot();
});
