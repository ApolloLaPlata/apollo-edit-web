// noticias_nav.js — Barra de navegação compartilhada entre as 13 páginas da Central de Notícias
// Detecta a página ativa pelo filename e gera os pills de navegação.

(function() {
    const menuItems = [
        { id: 'strategy', label: 'Estratégia', icon: 'fa-bullseye', color: '#E67E22' },
        { id: 'dashboard', label: 'Painel', icon: 'fa-desktop', color: '#3498DB' },
        { id: 'timeline', label: 'Timeline', icon: 'fa-stream', color: '#8b5cf6' },
        { id: 'images', label: 'Imagens', icon: 'fa-image', color: '#2ECC71' },
        { id: 'news', label: 'Notícias', icon: 'fa-fire', color: '#E74C3C' },
        { id: 'scripts', label: 'Roteiros', icon: 'fa-pen-nib', color: '#9B59B6' },
        { id: 'miner', label: 'Mineração', icon: 'fa-gem', color: '#E74C3C' },
        { id: 'radar', label: 'Radar YT', icon: 'fa-satellite-dish', color: '#F1C40F' },
        { id: 'studio', label: 'Estúdio', icon: 'fa-paint-brush', color: '#1ABC9C' },
        { id: 'channel', label: 'Meu Canal', icon: 'fa-tv', color: '#95A5A6' },
        { id: 'analytics', label: 'Analytics', icon: 'fa-chart-bar', color: '#E84393' },
        { id: 'monitor', label: 'Monitor', icon: 'fa-eye', color: '#00CEC9' },
        { id: 'history', label: 'Histórico', icon: 'fa-history', color: '#BDC3C7' },
        { id: 'autopilot', label: 'Copiloto Supremo', icon: 'fa-robot', color: '#8b5cf6' },
        { id: 'settings', label: 'Config', icon: 'fa-cog', color: '#7F8C8D' }
    ];

    // Detecta aba ativa baseado no filename
    const path = window.location.pathname;
    const match = path.match(/noticias_([a-zA-Z0-9_]+)\.html/);
    const activeTab = match ? match[1] : 'news';

    // Atualiza título da página
    const currentItem = menuItems.find(i => i.id === activeTab);
    const titleEl = document.getElementById('tool-title');
    if (currentItem && titleEl) {
        titleEl.innerHTML = `<i class="fas ${currentItem.icon}" style="color:${currentItem.color};"></i> ${currentItem.label}`;
    }

    // Gera a barra de navegação
    const navContainer = document.getElementById('noticias-nav');
    if (!navContainer) return;

    navContainer.innerHTML = menuItems.map(item => {
        const isActive = item.id === activeTab;
        return `
            <a href="noticias_${item.id}.html"
                class="noticias-nav-pill ${isActive ? 'active' : ''}"
                style="
                    ${isActive ? `background: ${item.color}; color: #000; border-color: transparent;` : `background: rgba(0,0,0,0.5); color: #fff; border-color: ${item.color};`}
                "
            >
                <i class="fas ${item.icon}"></i> ${item.label}
            </a>
        `;
    }).join('');

    // Função global para navegar entre abas (usado pelos logic files)
    window.switchTab = function(tabId) {
        window.location.href = `noticias_${tabId}.html`;
    };

    // Toast global simples
    window.showToast = function(msg, type) {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `apollo-toast ${type || 'info'}`;
        toast.innerHTML = `<span>${msg}</span>`;
        container.appendChild(toast);
        setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
    };

    // Helper global: monta o body correto para /api/noticias/ai
    window.buildNoticiasBody = function(extraFields) {
        return Object.assign({
            engine: localStorage.getItem('default_engine') || 'gemini',
            api_key_or: localStorage.getItem('openrouter_api_key') || '',
            api_key_grok: localStorage.getItem('api_key_grok') || ''
        }, extraFields || {});
    };

    // Helper: lê prefill de cross-page navigation e limpa
    window.readPrefill = function(key) {
        const data = localStorage.getItem(key);
        if (data) {
            localStorage.removeItem(key);
            try { return JSON.parse(data); } catch(e) { return data; }
        }
        return null;
    };
})();
