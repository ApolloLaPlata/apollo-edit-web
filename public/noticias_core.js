// noticias_core.js - Apollo Studio Integrado

document.addEventListener('DOMContentLoaded', () => {
    // Determine tab based on filename
    const path = window.location.pathname;
    let tab = 'news';
    const match = path.match(/noticias_([a-zA-Z0-9_]+)\.html/);
    if (match && match[1]) {
        tab = match[1];
    } else {
        const urlParams = new URLSearchParams(window.location.search);
        tab = urlParams.get('tab') || 'news';
    }
    
    const container = document.getElementById('tool-container');
    const title = document.getElementById('tool-title');

    const menuItems = [
        { id: 'strategy', label: 'Estratégia do Canal', icon: 'fa-bullseye', color: 'var(--btn-yellow)' },
        { id: 'dashboard', label: 'Painel Geral', icon: 'fa-desktop', color: 'var(--btn-green)' },
        { id: 'timeline', label: 'Mapeamento (Timeline)', icon: 'fa-stream', color: '#3498db' },
        { id: 'images', label: 'Buscador de Imagens', icon: 'fa-image', color: 'var(--btn-red)' },
        { id: 'news', label: 'Caçador de Notícias', icon: 'fa-fire', color: 'var(--btn-orange)' },
        { id: 'scripts', label: 'Roteiros', icon: 'fa-pen-nib', color: 'var(--btn-purple)' },
        { id: 'miner', label: 'Mineração Viral', icon: 'fa-gem', color: 'var(--btn-red)' },
        { id: 'radar', label: 'Radar YouTube', icon: 'fa-satellite-dish', color: '#F1C40F' },
        { id: 'studio', label: 'Estúdio de Imagens', icon: 'fa-paint-brush', color: '#1ABC9C' },
        { id: 'channel', label: 'Meu Canal', icon: 'fa-tv', color: '#95A5A6' },
        { id: 'analytics', label: 'Analytics', icon: 'fa-chart-bar', color: '#E84393' },
        { id: 'monitor', label: 'Monitor Ao Vivo', icon: 'fa-eye', color: '#00CEC9' },
        { id: 'history', label: 'Histórico', icon: 'fa-history', color: '#BDC3C7' },
        { id: 'settings', label: 'Configurações', icon: 'fa-cog', color: '#7F8C8D' }
    ];

    const currentItem = menuItems.find(i => i.id === tab);
    if (currentItem && title) {
        title.innerHTML = `<i class="fas ${currentItem.icon}" style="color:${currentItem.color};"></i> ${currentItem.label}`;
    }

    if (!container) return;

    // Generate Nav Menu
    const navHtml = `
        <div style="display:flex; gap:10px; overflow-x:auto; padding-bottom:15px; margin-bottom:20px; border-bottom:1px solid rgba(255,255,255,0.1);">
            ${menuItems.map(item => `
                <button 
                    onclick="window.location.href='noticias_${item.id}.html'" 
                    style="
                        background: ${item.id === tab ? item.color : 'rgba(0,0,0,0.5)'};
                        color: ${item.id === tab ? '#000' : '#fff'};
                        border: 1px solid ${item.id === tab ? 'transparent' : item.color};
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-weight: bold;
                        white-space: nowrap;
                        cursor: pointer;
                        transition: 0.2s;
                        font-family: 'Nunito', sans-serif;
                    "
                    onmouseover="this.style.transform='translateY(-2px)'"
                    onmouseout="this.style.transform='translateY(0)'"
                >
                    <i class="fas ${item.icon}"></i> ${item.label}
                </button>
            `).join('')}
        </div>
    `;

    // Generate Banners and React Root
    container.innerHTML = `
        ${navHtml}
        
        <div class="ad-slot" style="margin: 0 auto 20px auto; max-width: 728px; height: 90px; background: rgba(0,0,0,0.8); border: 2px dashed #555; display: flex; align-items: center; justify-content: center; color: #888; font-weight: bold;">
            <span>[ESPAÇO PUBLICITÁRIO - 728x90]</span>
        </div>

        <!-- DIV NATIVA EM VEZ DE IFRAME! Comunicação com HUD 100% garantida -->
        <div id="root" style="width:100%; min-height:800px; border: 4px solid #000; border-radius: 12px; box-shadow: 0 8px 0 rgba(0,0,0,0.8); background: #18181b; position: relative;"></div>

        <div class="ad-slot" style="margin: 20px auto 0 auto; max-width: 728px; height: 90px; background: rgba(0,0,0,0.8); border: 2px dashed #555; display: flex; align-items: center; justify-content: center; color: #888; font-weight: bold;">
            <span>[ESPAÇO PUBLICITÁRIO - 728x90]</span>
        </div>
    `;

    // Global variables for React to pick up
    window.__APOLLO_EMBEDDED__ = true;
    window.__APOLLO_TAB__ = tab;

    // Fetch the index.html from React Build to extract correct JS and CSS chunk names
    fetch('/ext_apps/central-das-noticias/dist/index.html')
        .then(res => res.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Extract CSS
            const links = doc.querySelectorAll('link[rel="stylesheet"]');
            links.forEach(link => {
                const href = link.getAttribute('href').replace('./', '/ext_apps/central-das-noticias/dist/');
                const newLink = document.createElement('link');
                newLink.rel = 'stylesheet';
                newLink.href = href;
                document.head.appendChild(newLink);
            });
            
            // Extract JS Module
            const scripts = doc.querySelectorAll('script[type="module"]');
            scripts.forEach(script => {
                const src = script.getAttribute('src').replace('./', '/ext_apps/central-das-noticias/dist/');
                const newScript = document.createElement('script');
                newScript.type = 'module';
                newScript.crossOrigin = 'anonymous';
                newScript.src = src;
                document.body.appendChild(newScript);
            });
        })
        .catch(err => console.error("Error loading React app natively:", err));
});
