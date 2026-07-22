/**
 * apollo_sfx.js
 * Injeta Efeitos Sonoros (SFX) para interações da UI usando Web Audio API
 */

document.addEventListener('DOMContentLoaded', () => {
    initApolloSFX();
});

// Singleton do AudioContext para evitar bloqueios de navegador
let audioCtx = null;

function initAudioContext() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
}

function initApolloSFX() {
    // Tenta inicializar no primeiro clique geral da página (política de navegadores)
    document.body.addEventListener('click', initAudioContext, { once: true });

    // Escuta cliques em todos os botões e links
    document.body.addEventListener('click', (e) => {
        const btn = e.target.closest('button, .btn, a.rpg-item');
        if (!btn) return;

        // Se for um botão de sucesso (verde/amarelo) ou resgate de Missão, toca o Som de Sucesso
        if (btn.classList.contains('yellow') || btn.classList.contains('ready') || btn.innerText.includes('RESGATAR')) {
            playSuccessSound();
        } else {
            // Som de clique genérico
            playClickSound();
        }
    }, true);
}

// Som de "Clique Tecnológico/Blip"
window.playClickSound = function() {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(800, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(300, audioCtx.currentTime + 0.1);

    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);

    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.1);
}

// Som de "Moeda/Sucesso" (Plim-Plim)
window.playSuccessSound = function() {
    if (!audioCtx) return;
    const osc1 = audioCtx.createOscillator();
    const osc2 = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    osc1.type = 'triangle';
    osc2.type = 'triangle';
    
    osc1.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
    osc2.frequency.setValueAtTime(1108.73, audioCtx.currentTime + 0.1); // C#6

    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.0, audioCtx.currentTime + 0.3);

    osc1.connect(gainNode);
    osc2.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc1.start(audioCtx.currentTime);
    osc1.stop(audioCtx.currentTime + 0.1);
    
    osc2.start(audioCtx.currentTime + 0.1);
    osc2.stop(audioCtx.currentTime + 0.3);
}

// Som de Arrastar (Swoosh suave para quando colocam item na Área de Transferência)
window.playDropSound = function() {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    osc.type = 'square';
    osc.frequency.setValueAtTime(150, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(50, audioCtx.currentTime + 0.2);

    gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);

    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.2);
}

// Erro
window.playErrorSound = function() {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(200, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(50, audioCtx.currentTime + 0.3);

    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.0, audioCtx.currentTime + 0.3);

    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.3);
}

// Nova Interface Consolidada (compatível com o App)
window.apolloSFX = {
    play: function(type) {
        initAudioContext();
        if (type === 'click') window.playClickSound();
        else if (type === 'success') window.playSuccessSound();
        else if (type === 'drop') window.playDropSound();
        else if (type === 'error') window.playErrorSound();
    }
};
