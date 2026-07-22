// tutorial.js - Sistema Global de Micro-Tutoriais Apollo Edit

const TUTORIAL_VIDEOS = {
    "hub.html": "dQw4w9WgXcQ", // Exemplo genérico
    "estudio.html": "jNQXAC9IVRw",
    "diretor.html": "tPEE9ZwTmy0",
    "roteiro.html": "V-_O7nl0Ii0",
    "oficina.html": "9bZkp7q19f0",
    "copilotos.html": "L_jWHffIx5E",
    "perfil.html": "3JZ_D3ELwOQ",
    "config.html": "2Vv-BfVoq4g"
};

function initTutorialSystem() {
    // 1. Determina a página atual
    const path = window.location.pathname;
    const page = path.split('/').pop() || 'hub.html';
    
    // Fallback genérico se a página não estiver mapeada
    const videoId = TUTORIAL_VIDEOS[page] || "dQw4w9WgXcQ";

    // 2. Injeta CSS para o Botão e Modal
    const style = document.createElement('style');
    style.innerHTML = `
        .tutorial-floating-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #FFD32A 0%, #F39C12 100%);
            border: 3px solid #000;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5), 0 0 20px rgba(250, 204, 21, 0.4);
            z-index: 9998;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .tutorial-floating-btn:hover {
            transform: scale(1.1) rotate(10deg);
            box-shadow: 0 5px 20px rgba(0,0,0,0.6), 0 0 30px rgba(250, 204, 21, 0.6);
        }
        .tutorial-modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 9999;
            display: none;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(10px);
        }
        .tutorial-modal-content {
            background: #111;
            border: 4px solid var(--btn-purple, #9B59B6);
            border-radius: 16px;
            padding: 20px;
            width: 80%;
            max-width: 900px;
            position: relative;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        }
        .tutorial-close-btn {
            position: absolute;
            top: -20px;
            right: -20px;
            width: 40px;
            height: 40px;
            background: #f87171;
            border: 3px solid #000;
            border-radius: 50%;
            color: #fff;
            font-weight: bold;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        .tutorial-close-btn:hover { background: #ef4444; }
        .tutorial-iframe-wrapper {
            position: relative;
            padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
            height: 0;
            overflow: hidden;
            border-radius: 8px;
            background: #000;
        }
        .tutorial-iframe-wrapper iframe {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            border: none;
        }
        .tutorial-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-family: 'Bangers', cursive;
            color: #fff;
            letter-spacing: 1px;
        }
    `;
    document.head.appendChild(style);

    // 3. Cria o Botão Flutuante
    const btn = document.createElement('div');
    btn.className = 'tutorial-floating-btn';
    btn.innerHTML = '📺';
    btn.title = 'Como usar esta aba (Tutorial)';
    document.body.appendChild(btn);

    // 4. Cria o Modal
    const modal = document.createElement('div');
    modal.className = 'tutorial-modal-overlay';
    modal.innerHTML = `
        <div class="tutorial-modal-content">
            <button class="tutorial-close-btn">X</button>
            <div class="tutorial-header">
                <h2 style="margin:0; font-size: 2rem;">TUTORIAL: ${page.toUpperCase()}</h2>
                <div style="background: rgba(250,204,21,0.2); color: #FFD32A; padding: 5px 10px; border-radius: 4px; font-family: 'Nunito', sans-serif; font-size: 0.9rem;">
                    Curso Avançado de API em breve!
                </div>
            </div>
            <div class="tutorial-iframe-wrapper">
                <iframe id="tutorial-iframe" src="" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // 5. Lógica de Interação
    btn.addEventListener('click', () => {
        // Carrega o SRC só quando abrir para economizar banda
        const iframe = document.getElementById('tutorial-iframe');
        iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
        modal.style.display = 'flex';
    });

    const closeBtn = modal.querySelector('.tutorial-close-btn');
    closeBtn.addEventListener('click', () => {
        const iframe = document.getElementById('tutorial-iframe');
        iframe.src = ""; // Para o vídeo
        modal.style.display = 'none';
    });

    // Fecha clicando fora
    modal.addEventListener('click', (e) => {
        if(e.target === modal) {
            const iframe = document.getElementById('tutorial-iframe');
            iframe.src = ""; 
            modal.style.display = 'none';
        }
    });
}

document.addEventListener('DOMContentLoaded', initTutorialSystem);
