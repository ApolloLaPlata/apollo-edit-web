// dashboard_logic.js - Lógica para o Painel Geral (tab-dashboard)

let dashboardCategory = 'Geral';
let dashboardNews = [];
let isFetchingDashboard = false;

document.addEventListener('DOMContentLoaded', () => {
    renderDashboardCategories();
    // Carregar inicialmente
    setTimeout(() => loadDashboardNews('Geral'), 300);
});

function renderDashboardCategories() {
    const container = document.getElementById('dashboard-categories');
    if (!container) return;
    
    const categories = ['Geral', 'Política', 'Economia', 'Mundo', 'Tecnologia', 'Entretenimento'];
    container.innerHTML = '';
    
    categories.forEach(cat => {
        const btn = document.createElement('button');
        
        if (dashboardCategory === cat) {
            btn.style.cssText = 'padding: 6px 16px; border-radius: 9999px; font-size: 14px; font-weight: 600; white-space: nowrap; transition: all 0.2s; cursor: pointer; background: #FFD32A; color: #000; border: 1px solid #FFD32A;';
        } else {
            btn.style.cssText = 'padding: 6px 16px; border-radius: 9999px; font-size: 14px; font-weight: 500; white-space: nowrap; transition: all 0.2s; cursor: pointer; background: rgba(0,0,0,0.4); border: 1px solid #444; color: #cbd5e1;';
            btn.onmouseover = () => btn.style.backgroundColor = '#333';
            btn.onmouseout = () => btn.style.backgroundColor = 'rgba(0,0,0,0.4)';
        }
        
        btn.textContent = cat;
        btn.onclick = () => loadDashboardNews(cat);
        
        container.appendChild(btn);
    });
}

async function loadDashboardNews(category) {
    if (isFetchingDashboard) return;
    
    dashboardCategory = category;
    renderDashboardCategories(); // Atualiza botões
    
    isFetchingDashboard = true;
    dashboardNews = [];
    
    const grid = document.getElementById('dashboard-grid');
    const loading = document.getElementById('dashboard-loading');
    const errorBox = document.getElementById('dashboard-error');
    const errorText = document.getElementById('dashboard-error-text');
    
    grid.innerHTML = '';
    errorBox.style.display = 'none';
    loading.style.display = 'flex';
    
    let topic = category === 'Geral' ? 'Principais notícias do dia Brasil e Mundo' : category;
    
    try {
        const response = await fetch('https://api.apolloedit.com/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt_type: 'cacar',
                input_text: topic,
                news_count: 12,
                engine: localStorage.getItem('default_engine') || 'gemini',
                api_key_or: localStorage.getItem('openrouter_api_key') || '',
                api_key_grok: localStorage.getItem('api_key_grok') || ''
            })
        });

        if (!response.ok) throw new Error(`Erro API: ${response.status}`);
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        let cleanText = (data.text || data.content || '[]').replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
        dashboardNews = JSON.parse(cleanText);
        
        renderDashboardGrid();
        
    } catch (err) {
        errorText.textContent = err.message || "Erro ao carregar notícias do painel.";
        errorBox.style.display = 'block';
    } finally {
        isFetchingDashboard = false;
        loading.style.display = 'none';
    }
}

function renderDashboardGrid() {
    const grid = document.getElementById('dashboard-grid');
    grid.innerHTML = '';
    
    if (dashboardNews.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; color: #71717a; padding: 40px;">Nenhuma notícia encontrada.</div>';
        return;
    }
    
    dashboardNews.forEach(item => {
        const card = document.createElement('div');
        // Mantendo os botões violeta
        card.style.cssText = 'background: #1e1e1e; border-radius: 12px; border: 1px solid #333; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 8px rgba(0,0,0,0.3);';
        
        // Hover effect on card
        card.onmouseover = () => {
            card.style.transform = 'translateY(-2px)';
            card.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)';
        };
        card.onmouseout = () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
        };

        const imageHtml = item.imageUrl 
            ? `<img src="${item.imageUrl}" alt="${item.title}" style="width: 100%; height: 192px; object-fit: cover; border-bottom: 1px solid #333;" />`
            : `<div style="width: 100%; height: 192px; background: #2a2a2a; display: flex; align-items: center; justify-content: center; border-bottom: 1px solid #333;">
                 <i class="fas fa-image" style="font-size: 32px; color: #555;"></i>
               </div>`;

        // Violet color for source and buttons instead of indigo: #8b5cf6
        card.innerHTML = `
            ${imageHtml}
            <div style="padding: 20px; display: flex; flex-direction: column; flex: 1;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; font-size: 12px;">
                    <span style="font-weight: 600; color: #a78bfa; background: rgba(139,92,246,0.15); padding: 4px 10px; border-radius: 9999px;">${item.source}</span>
                    <div style="display: flex; align-items: center; gap: 4px; color: #71717a;">
                        <i class="far fa-clock"></i> ${item.date || 'Hoje'}
                    </div>
                </div>
                
                <h3 style="font-size: 16px; font-weight: 700; color: #fff; margin: 0 0 8px 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                    ${item.title}
                </h3>
                
                <p style="font-size: 14px; color: #94a3b8; margin: 0 0 16px 0; line-height: 1.5; flex: 1;">
                    ${item.summary}
                </p>
                
                <div style="display: flex; gap: 8px; margin-top: auto;">
                    <a href="${item.url}" target="_blank" rel="noopener noreferrer" style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 8px 16px; background: rgba(0,0,0,0.3); border: 1px solid #444; color: #cbd5e1; border-radius: 8px; font-size: 14px; font-weight: 500; text-decoration: none; transition: background 0.2s;" onmouseover="this.style.background='#333'" onmouseout="this.style.background='rgba(0,0,0,0.3)'">
                        <i class="fas fa-external-link-alt"></i> Ler Notícia
                    </a>
                    
                    <button onclick="sendDashboardToScripts('${encodeURIComponent(item.title)}', '${encodeURIComponent(item.summary)}')" style="display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: rgba(139,92,246,0.15); color: #a78bfa; border: none; border-radius: 8px; cursor: pointer; transition: background 0.2s;" title="Criar Roteiro" onmouseover="this.style.background='rgba(139,92,246,0.3)'" onmouseout="this.style.background='rgba(139,92,246,0.15)'">
                        <i class="fas fa-pen"></i>
                    </button>
                </div>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

function sendDashboardToScripts(encTitle, encSummary) {
    const title = decodeURIComponent(encTitle);
    const summary = decodeURIComponent(encSummary);
    
    localStorage.setItem('scripts_prefill', JSON.stringify({
        text: `Notícia: ${title}\nResumo: ${summary}\n\nFaça um vídeo sobre isso.`
    }));
    window.location.href = 'noticias_scripts.html';
}

function copyDashboardNews() {
    if (dashboardNews.length === 0) return;
    
    const textToCopy = dashboardNews.map((item) => {
        return `Título: ${item.title}\nResumo: ${item.summary}\nFonte: ${item.source}\nLink: ${item.url}`;
    }).join('\n\n---\n\n');
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        showToast('Notícias copiadas!', 'success');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showToast('Erro ao copiar', 'error');
    });
}
