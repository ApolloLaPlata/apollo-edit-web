/**
 * Apollo La Plata - Copilot Engine
 * Controla o balão de fala do Mascote Apollo e a UI flutuante.
 */

window.apolloCopilot = {
    kb: window.apolloCopilotKB,
    
    init: function() {
        if (document.getElementById('apollo-copilot-widget')) return; // Already injected

        const style = document.createElement('style');
        style.innerHTML = `
            #apollo-copilot-widget {
                position: fixed;
                bottom: -200px; /* Hide initially */
                left: 20px;
                z-index: 10000;
                display: flex;
                align-items: flex-end;
                gap: 15px;
                transition: bottom 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                pointer-events: none;
            }
            #apollo-copilot-widget.show {
                bottom: 20px;
            }
            #apollo-copilot-avatar {
                width: 100px;
                height: 100px;
                object-fit: contain;
                animation: float 3s ease-in-out infinite;
                filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.5));
                pointer-events: auto; /* Pode ser clicado se quisermos */
            }
            #apollo-copilot-bubble {
                background: white;
                color: #0f172a;
                padding: 15px 20px;
                border-radius: 16px;
                border-bottom-left-radius: 0;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
                font-size: 0.9rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                max-width: 280px;
                position: relative;
                pointer-events: auto;
            }
            #apollo-copilot-bubble::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: -10px;
                border-width: 10px 10px 0 0;
                border-style: solid;
                border-color: white transparent transparent transparent;
            }
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
                100% { transform: translateY(0px); }
            }
            
            /* Responsive Hide on very small screens to avoid clutter */
            @media (max-width: 768px) {
                #apollo-copilot-widget {
                    transform: scale(0.8);
                    transform-origin: bottom left;
                }
            }
        `;
        document.head.appendChild(style);

        const widget = document.createElement('div');
        widget.id = 'apollo-copilot-widget';
        widget.innerHTML = `
            <img id="apollo-copilot-avatar" src="mascote_piloto_1780233498071.png" alt="Apollo Copilot">
            <div id="apollo-copilot-bubble">Olá, piloto!</div>
        `;
        document.body.appendChild(widget);
        this.widget = widget;
        this.bubble = document.getElementById('apollo-copilot-bubble');
        this.timeout = null;

        // Saudação Inicial (50% de chance para não ficar irritante toda vez que navega)
        if (Math.random() > 0.5) {
            setTimeout(() => { this.react("login"); }, 1000);
        }
    },

    react: function(actionType) {
        if (!this.kb || !this.kb[actionType]) return;
        
        const lines = this.kb[actionType];
        const randomLine = lines[Math.floor(Math.random() * lines.length)];
        
        this.bubble.innerText = randomLine;
        this.widget.classList.add('show');
        
        if (window.apolloSFX) {
            // Se for erro, toca algo diferente
            if (actionType.includes("error") || actionType === "low_gas") {
                window.apolloSFX.play('error');
            } else {
                window.apolloSFX.play('success'); // Toca pop up amigável
            }
        }
        
        if (this.timeout) clearTimeout(this.timeout);
        this.timeout = setTimeout(() => {
            this.widget.classList.remove('show');
        }, 5000);
    }
};

// Iniciar se o KB existir
document.addEventListener('DOMContentLoaded', () => {
    if (window.apolloCopilotKB) {
        window.apolloCopilot.init();
    }
});
