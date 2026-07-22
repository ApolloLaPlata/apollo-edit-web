// ==========================================
// APOLLO VISUALIZADOR UNIVERSAL
// ==========================================

class ApolloVisualizador {
    constructor() {
        this.instances = {}; // Armazena instâncias ativas
        this.zIndexCounter = 1000;
        this.initCSS();
    }

    initCSS() {
        if (document.getElementById('apollo-visualizador-css')) return;
        const style = document.createElement('style');
        style.id = 'apollo-visualizador-css';
        style.innerHTML = `
            .apollo-visualizador {
                position: fixed;
                background: rgba(15, 15, 20, 0.95);
                border: 2px solid #a855f7;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 20px rgba(168, 85, 247, 0.3);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                backdrop-filter: blur(10px);
                transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.3s;
                resize: both;
            }
            .apollo-visualizador.minimized {
                width: 60px !important;
                height: 60px !important;
                border-radius: 50% !important;
                resize: none;
                overflow: hidden;
                cursor: pointer;
                border: 3px solid #facc15;
                box-shadow: 0 0 15px #facc15;
                animation: floatBubble 3s ease-in-out infinite;
            }
            @keyframes floatBubble {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
                100% { transform: translateY(0px); }
            }
            .apollo-visualizador-header {
                height: 35px;
                background: linear-gradient(90deg, #3b0764, #581c87);
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 10px;
                cursor: grab;
                user-select: none;
            }
            .apollo-visualizador-header:active {
                cursor: grabbing;
            }
            .apollo-visualizador.minimized .apollo-visualizador-header {
                display: none;
            }
            .apollo-title {
                color: #fff;
                font-family: 'Bangers', cursive;
                font-size: 1.2rem;
                letter-spacing: 1px;
                pointer-events: none;
            }
            .apollo-controls {
                display: flex;
                gap: 8px;
            }
            .apollo-ctrl-btn {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                transition: 0.2s;
            }
            .apollo-btn-min { background: #facc15; color: #000; }
            .apollo-btn-close { background: #ef4444; color: #fff; }
            .apollo-btn-min:hover { filter: brightness(1.2); transform: scale(1.1); }
            .apollo-btn-close:hover { filter: brightness(1.2); transform: scale(1.1); }
            
            .apollo-content {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #000;
                overflow: hidden;
                position: relative;
            }
            .apollo-visualizador.minimized .apollo-content {
                pointer-events: none;
            }
            .apollo-media {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
            }
            .apollo-visualizador.minimized .apollo-media {
                object-fit: cover;
                width: 100%;
                height: 100%;
            }
            
            /* Classe injetada no Bagageiro quando em uso */
            .bagageiro-item-em-uso {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 15px rgba(59, 130, 246, 0.8) !important;
                background: rgba(59, 130, 246, 0.2) !important;
                transition: 0.3s;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Abre um arquivo no visualizador
     * @param {string} url URL do arquivo
     * @param {string} type 'image', 'video', 'audio', etc
     * @param {string} title Título da janela
     * @param {string} bagageiroId ID do DOM do item no bagageiro para sincronizar cor
     */
    open(url, type, title = 'Visualizador', bagageiroId = null) {
        const id = 'vis_' + Math.random().toString(36).substr(2, 9);
        
        const win = document.createElement('div');
        win.id = id;
        win.className = 'apollo-visualizador';
        win.style.zIndex = this.zIndexCounter++;
        
        // Tamanho inicial baseado no tipo (poderia ser mais inteligente e ler proporção real)
        if(type === 'video') {
            win.style.width = '400px';
            win.style.height = '700px'; // Assumindo vertical por padrão para Shorts
        } else {
            win.style.width = '600px';
            win.style.height = '400px';
        }
        
        // Posição inicial centralizada
        win.style.left = (window.innerWidth / 2 - parseInt(win.style.width)/2) + 'px';
        win.style.top = (window.innerHeight / 2 - parseInt(win.style.height)/2) + 'px';

        let contentHtml = '';
        if (type === 'image') {
            contentHtml = `<img src="${url}" class="apollo-media" draggable="false">`;
        } else if (type === 'video') {
            contentHtml = `<video src="${url}" class="apollo-media" controls autoplay loop></video>`;
        } else if (type === 'audio') {
            contentHtml = `
                <div style="padding:20px; text-align:center; color:#fff;">
                    <div style="font-size:3rem; margin-bottom:10px;">🎵</div>
                    <audio src="${url}" controls autoplay></audio>
                </div>`;
        } else if (type === 'editor') {
            contentHtml = `<iframe src="${url}" style="width:100%; height:100%; border:none;"></iframe>`;
        } else {
            contentHtml = `<div style="color:#fff; padding:20px;">Iframe / Objeto: <br>${url}</div>`;
        }

        win.innerHTML = `
            <div class="apollo-visualizador-header">
                <span class="apollo-title">${title}</span>
                <div class="apollo-controls">
                    <button class="apollo-ctrl-btn apollo-btn-min" title="Minimizar (Bolinha)">_</button>
                    <button class="apollo-ctrl-btn apollo-btn-close" title="Fechar">X</button>
                </div>
            </div>
            <div class="apollo-content">
                ${contentHtml}
            </div>
        `;

        document.body.appendChild(win);

        // Highlight no Bagageiro
        if (bagageiroId) {
            const bagItem = document.getElementById(bagageiroId);
            if (bagItem) bagItem.classList.add('bagageiro-item-em-uso');
        }

        this.instances[id] = { el: win, bagageiroId, state: 'normal', originalRect: null };

        this.setupEvents(id);
        return id;
    }

    setupEvents(id) {
        const inst = this.instances[id];
        const win = inst.el;
        const header = win.querySelector('.apollo-visualizador-header');
        const btnMin = win.querySelector('.apollo-btn-min');
        const btnClose = win.querySelector('.apollo-btn-close');

        // Fazer a janela subir de Z-Index ao clicar
        win.addEventListener('mousedown', () => {
            win.style.zIndex = this.zIndexCounter++;
        });

        // Minimização (Bolinha)
        btnMin.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMinimize(id);
        });

        // Restaurar ao clicar se for bolinha
        win.addEventListener('click', (e) => {
            if (inst.state === 'minimized') {
                this.toggleMinimize(id);
            }
        });

        // Fechar
        btnClose.addEventListener('click', (e) => {
            e.stopPropagation();
            this.close(id);
        });

        // DRAG AND DROP
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;

        const onMouseMove = (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            win.style.left = (initialLeft + dx) + 'px';
            win.style.top = (initialTop + dy) + 'px';
        };

        const onMouseUp = () => {
            isDragging = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        header.addEventListener('mousedown', (e) => {
            if (inst.state === 'minimized') return;
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = win.offsetLeft;
            initialTop = win.offsetTop;
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        // Drag da bolinha também funciona
        win.addEventListener('mousedown', (e) => {
            if (inst.state !== 'minimized') return;
            // Se clicar na bolinha para arrastar
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = win.offsetLeft;
            initialTop = win.offsetTop;
            
            // Variável para não disparar o click (restore) se for só drag
            inst.didDrag = false;

            const onMouseMoveBubble = (ev) => {
                if (!isDragging) return;
                const dx = ev.clientX - startX;
                const dy = ev.clientY - startY;
                if (Math.abs(dx) > 5 || Math.abs(dy) > 5) inst.didDrag = true;
                win.style.left = (initialLeft + dx) + 'px';
                win.style.top = (initialTop + dy) + 'px';
            };

            const onMouseUpBubble = () => {
                isDragging = false;
                document.removeEventListener('mousemove', onMouseMoveBubble);
                document.removeEventListener('mouseup', onMouseUpBubble);
                // Reseta a flag apos um pequeno delay para não interferir com o evento de click
                setTimeout(() => inst.didDrag = false, 50);
            };

            document.addEventListener('mousemove', onMouseMoveBubble);
            document.addEventListener('mouseup', onMouseUpBubble);
        });

        // Sobrescrever click da janela para prevenir restore se estiver arrastando a bolinha
        win.addEventListener('click', (e) => {
            if (inst.state === 'minimized') {
                if (inst.didDrag) {
                    e.stopPropagation();
                    return; // Nao restaura
                }
            }
        }, true);
    }

    toggleMinimize(id) {
        const inst = this.instances[id];
        const win = inst.el;
        if (inst.state === 'normal') {
            inst.originalRect = {
                width: win.style.width,
                height: win.style.height
            };
            win.classList.add('minimized');
            inst.state = 'minimized';
        } else {
            win.style.width = inst.originalRect.width;
            win.style.height = inst.originalRect.height;
            win.classList.remove('minimized');
            inst.state = 'normal';
        }
    }

    close(id) {
        const inst = this.instances[id];
        if (!inst) return;
        
        // Remover highlight do Bagageiro
        if (inst.bagageiroId) {
            const bagItem = document.getElementById(inst.bagageiroId);
            if (bagItem) bagItem.classList.remove('bagageiro-item-em-uso');
        }

        inst.el.remove();
        delete this.instances[id];
    }
}

// Instanciar globalmente
window.Visualizador = new ApolloVisualizador();
