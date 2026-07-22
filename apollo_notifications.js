/**
 * apollo_notifications.js
 * Injeta o sino de notificações de forma global no cabeçalho.
 */

document.addEventListener('DOMContentLoaded', () => {
    injectNotificationSystem();
});

function injectNotificationSystem() {
    const userWidget = document.querySelector('.user-widget');
    if (!userWidget) return; // Se não houver cabeçalho padrão, ignora

    // CSS para as animações e layout
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes bellRing {
            0%, 100% { transform: rotate(0deg); }
            20% { transform: rotate(15deg); }
            40% { transform: rotate(-15deg); }
            60% { transform: rotate(10deg); }
            80% { transform: rotate(-10deg); }
        }
        .bell-ringing {
            animation: bellRing 0.6s ease-in-out;
            color: var(--btn-yellow, #facc15) !important;
        }
        .notif-dot {
            position: absolute;
            top: -2px;
            right: -2px;
            width: 10px;
            height: 10px;
            background: var(--btn-red, #ef4444);
            border-radius: 50%;
            border: 2px solid #1e1e1e;
            display: none;
            box-shadow: 0 0 8px var(--btn-red);
        }
        .notif-dropdown {
            position: absolute;
            top: 50px;
            right: 0;
            width: 300px;
            background: #111;
            border: 2px solid #444;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.8);
            display: none;
            flex-direction: column;
            z-index: 10000;
        }
        .notif-dropdown-header {
            padding: 10px 15px;
            background: #222;
            border-bottom: 1px solid #444;
            font-family: 'Bangers', cursive;
            font-size: 1.2rem;
            color: #fff;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            display: flex;
            justify-content: space-between;
        }
        .notif-dropdown-body {
            max-height: 300px;
            overflow-y: auto;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .notif-item {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 6px;
            border-left: 3px solid var(--btn-purple, #8b5cf6);
            font-size: 0.85rem;
            color: #ddd;
        }
        .notif-item.unread {
            background: rgba(139, 92, 246, 0.15);
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);

    // Estrutura HTML do Sino
    const notifContainer = document.createElement('div');
    notifContainer.id = 'apollo-notif-container';
    notifContainer.style = 'position: relative; margin-right: 15px;';
    
    notifContainer.innerHTML = `
        <button id="apollo-bell-btn" style="background: none; border: none; font-size: 1.5rem; color: #aaa; cursor: pointer; position: relative; transition: color 0.3s;">
            🔔
            <div id="apollo-notif-dot" class="notif-dot"></div>
        </button>
        <div id="apollo-notif-dropdown" class="notif-dropdown">
            <div class="notif-dropdown-header">
                <span>NOTIFICAÇÕES</span>
                <button onclick="clearNotifications()" style="background:none; border:none; color:var(--btn-yellow); cursor:pointer; font-size:0.8rem;">Limpar</button>
            </div>
            <div class="notif-dropdown-body" id="apollo-notif-list">
                <div style="text-align: center; color: #666; padding: 20px;">Sem alertas no momento.</div>
            </div>
        </div>
    `;

    userWidget.insertBefore(notifContainer, userWidget.firstChild);

    // Lógica do Clique
    const bellBtn = document.getElementById('apollo-bell-btn');
    const dropdown = document.getElementById('apollo-notif-dropdown');
    const dot = document.getElementById('apollo-notif-dot');

    bellBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isVisible = dropdown.style.display === 'flex';
        dropdown.style.display = isVisible ? 'none' : 'flex';
        if (!isVisible) {
            dot.style.display = 'none'; // Marca como lido visualmente
        }
    });

    document.addEventListener('click', (e) => {
        if (!notifContainer.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

window.triggerNotification = function(message, type = 'info') {
    const list = document.getElementById('apollo-notif-list');
    const bell = document.getElementById('apollo-bell-btn');
    const dot = document.getElementById('apollo-notif-dot');
    
    if (!list) return;

    // Remove mensagem de "vazio"
    if (list.innerHTML.includes('Sem alertas')) {
        list.innerHTML = '';
    }

    let color = 'var(--btn-purple)';
    if (type === 'success') color = 'var(--btn-green)';
    if (type === 'error') color = 'var(--btn-red)';
    if (type === 'warning') color = 'var(--btn-yellow)';

    const item = document.createElement('div');
    item.className = 'notif-item unread';
    item.style.borderLeftColor = color;
    item.innerHTML = `<span>${message}</span>`;
    
    list.insertBefore(item, list.firstChild);

    // Anima o sino
    bell.classList.add('bell-ringing');
    dot.style.display = 'block';

    setTimeout(() => {
        bell.classList.remove('bell-ringing');
    }, 600);

    // Playzinho sonoro sutil (opcional/mock)
    console.log('[NOTIFICAÇÃO] ' + message);
}

window.apolloNotifications = {
    add: function(title, message, type = 'info') {
        const fullMessage = `<strong>${title}</strong>: ${message}`;
        window.triggerNotification(fullMessage, type);
    }
};

window.clearNotifications = function() {
    const list = document.getElementById('apollo-notif-list');
    if (list) {
        list.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">Sem alertas no momento.</div>';
    }
}
