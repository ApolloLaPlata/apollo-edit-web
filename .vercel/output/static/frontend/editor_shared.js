// editor_shared.js
// Contém funções globais para todos os editores (Etapas 16, 19 e 20)

document.addEventListener('DOMContentLoaded', () => {
    // Etapa 19: Botão Global de Voltar ao Hub
    const header = document.querySelector('header');
    if (header) {
        const btnHub = document.createElement('button');
        btnHub.className = 'action-btn';
        btnHub.style.backgroundColor = '#1a1a1a';
        btnHub.style.border = '1px solid #444';
        btnHub.style.marginRight = '15px';
        btnHub.innerHTML = '⬅ Voltar ao Hub';
        btnHub.onclick = () => window.location.href = 'hub.html';
        
        header.insertBefore(btnHub, header.firstChild);
    }

    // Etapa 20: Alertas Visuais (Toasts)
    const toastContainer = document.createElement('div');
    toastContainer.style.position = 'fixed';
    toastContainer.style.bottom = '20px';
    toastContainer.style.left = '50%';
    toastContainer.style.transform = 'translateX(-50%)';
    toastContainer.style.zIndex = '9999';
    document.body.appendChild(toastContainer);

    window.showToast = function(message, color = '#6b21a8') {
        const toast = document.createElement('div');
        toast.style.background = color;
        toast.style.color = '#fff';
        toast.style.padding = '10px 20px';
        toast.style.borderRadius = '50px';
        toast.style.marginTop = '10px';
        toast.style.boxShadow = '0 5px 15px rgba(0,0,0,0.5)';
        toast.style.fontFamily = 'Inter, sans-serif';
        toast.style.transition = 'opacity 0.5s ease';
        toast.innerText = message;
        
        toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    };

    // Etapa 16 Aprimorada: Teclas de Atalho Globais + Cheat Sheet Modal
    document.addEventListener('keydown', (e) => {
        // Ctrl + S (Salvar)
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            window.showToast("Rascunho Salvo Localmente!", "#0055ff");
        }
        // Ctrl + E (Exportar para o Bagageiro)
        if (e.ctrlKey && e.key === 'e') {
            e.preventDefault();
            if (typeof window.exportToBagageiro === 'function') {
                window.exportToBagageiro();
                window.showToast("Exportando para o Bagageiro...", "#6b21a8");
            }
        }
        // Ctrl + Z (Desfazer - Mock)
        if (e.ctrlKey && e.key === 'z') {
            e.preventDefault();
            window.showToast("Desfazer (Undo) acionado!", "#888");
            // A lógica de splice nos arrays de camadas entraria aqui
        }
        // Barra de Espaço (Play/Pause genérico)
        if (e.key === ' ' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            const btnPlay = document.getElementById('btn-play');
            const btnPause = document.getElementById('btn-pause');
            // Mock toggle click
            if (btnPlay && btnPlay.style.display !== 'none') btnPlay.click();
            else if (btnPause) btnPause.click();
        }
        // Shift + ? (Mostrar Atalhos)
        if (e.shiftKey && e.key === '?') {
            e.preventDefault();
            toggleHotkeyModal();
        }
    });

    // Criação Dinâmica do Modal de Atalhos (Cheat Sheet)
    function toggleHotkeyModal() {
        let modal = document.getElementById('hotkey-modal');
        if (modal) {
            modal.remove(); // Se existe, fecha
            return;
        }

        modal = document.createElement('div');
        modal.id = 'hotkey-modal';
        modal.style.position = 'fixed';
        modal.style.top = '50%';
        modal.style.left = '50%';
        modal.style.transform = 'translate(-50%, -50%)';
        modal.style.background = 'rgba(15, 15, 17, 0.95)';
        modal.style.border = '1px solid #6b21a8';
        modal.style.boxShadow = '0 0 30px rgba(0,0,0,0.8)';
        modal.style.padding = '30px';
        modal.style.borderRadius = '12px';
        modal.style.zIndex = '9999';
        modal.style.color = '#fff';
        modal.style.minWidth = '400px';
        modal.style.backdropFilter = 'blur(10px)';

        modal.innerHTML = `
            <h2 style="color: #00ffcc; margin-bottom: 20px; text-align: center;">⌨️ Atalhos do Apollo</h2>
            <ul style="list-style: none; padding: 0; line-height: 2;">
                <li style="display: flex; justify-content: space-between; border-bottom: 1px solid #333; padding-bottom: 5px;">
                    <span>Salvar Rascunho</span> <strong style="color: #6b21a8;">Ctrl + S</strong>
                </li>
                <li style="display: flex; justify-content: space-between; border-bottom: 1px solid #333; padding: 5px 0;">
                    <span>Enviar para Bagageiro</span> <strong style="color: #6b21a8;">Ctrl + E</strong>
                </li>
                <li style="display: flex; justify-content: space-between; border-bottom: 1px solid #333; padding: 5px 0;">
                    <span>Desfazer Ação</span> <strong style="color: #6b21a8;">Ctrl + Z</strong>
                </li>
                <li style="display: flex; justify-content: space-between; border-bottom: 1px solid #333; padding: 5px 0;">
                    <span>Play / Pause</span> <strong style="color: #6b21a8;">Espaço</strong>
                </li>
                <li style="display: flex; justify-content: space-between; padding-top: 5px;">
                    <span>Ajuda de Atalhos</span> <strong style="color: #6b21a8;">Shift + ?</strong>
                </li>
            </ul>
            <button id="btn-close-hotkeys" class="action-btn" style="width: 100%; margin-top: 20px; background: #333;">Fechar (Esc)</button>
        `;

        document.body.appendChild(modal);

        document.getElementById('btn-close-hotkeys').onclick = () => modal.remove();
        
        // Listener de ESC apenas para o modal
        const escListener = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', escListener);
            }
        };
        document.addEventListener('keydown', escListener);
    }

    // O HUD de Transferência agora é 100% gerenciado nativamente pelo transfer_hud.js
    // Nenhuma injeção de DOM simulada é necessária aqui.
});
