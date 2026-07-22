document.addEventListener('DOMContentLoaded', () => {
    
    // --- Lógica de Temas do Fundo 3D ---
    const path = window.location.pathname.toLowerCase();
    let theme = {
        bgTop: '#130a2a',
        bgBottom: '#0f0518',
        grid: 'rgba(155, 89, 182, 0.15)' // Roxo Padrão (Hub/Geral)
    };

    if (path.includes('midia')) {
        // Azul Cyan
        theme = { bgTop: '#0a192f', bgBottom: '#020c1b', grid: 'rgba(100, 255, 218, 0.15)' };
    } else if (path.includes('volume') || path.includes('musica')) {
        // Rosa Neon
        theme = { bgTop: '#2d0a1b', bgBottom: '#1a050f', grid: 'rgba(255, 105, 180, 0.15)' };
    } else if (path.includes('dublagem') || path.includes('tts') || path.includes('podcast') || path.includes('narrador')) {
        // Laranja/Vermelho (Vozes)
        theme = { bgTop: '#2a110a', bgBottom: '#180805', grid: 'rgba(255, 140, 0, 0.15)' };
    } else if (path.includes('montador') || path.includes('timeline')) {
        // Amarelo/Preto (Edição)
        theme = { bgTop: '#1a1a1a', bgBottom: '#0d0d0d', grid: 'rgba(255, 211, 42, 0.15)' };
    } else if (path.includes('tanque') || path.includes('dashboard') || path.includes('fila')) {
        // Verde Matrix (Recursos)
        theme = { bgTop: '#0a2a16', bgBottom: '#05180c', grid: 'rgba(74, 222, 128, 0.15)' };
    }

    const bg = document.getElementById('global-3d-bg');
    if(bg) {
        bg.style.setProperty('--theme-bg-top', theme.bgTop);
        bg.style.setProperty('--theme-bg-bottom', theme.bgBottom);
        bg.style.setProperty('--theme-grid-color', theme.grid);
    }

    // --- Efeito Parallax Mouse ---
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        
        const rotX = (y - 0.5) * 10;
        const rotY = (x - 0.5) * 10;
        
        if(bg) {
            bg.style.setProperty('--mouseX', rotY);
            bg.style.setProperty('--mouseY', -rotX);
        }
    });

    // Injetar Carrinhos Pixel Art (Decorativos) - Removido a pedido do usuário
    const cars = [];


    // Animações inline
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes float {
            0% { transform: translateY(0px) rotate(5deg); }
            50% { transform: translateY(-20px) rotate(-5deg); }
            100% { transform: translateY(0px) rotate(5deg); }
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0) scaleX(-1); }
            50% { transform: translateY(-10px) scaleX(-1); }
        }
    `;
    document.head.appendChild(style);
});
