// monitor_logic.js - Lógica para a aba Monitor Ao Vivo

let isMonitoringProfile = false;
let currentMonitorData = null;

async function handleStartMonitoring() {
    const urlInput = document.getElementById('monitor-url');
    const url = urlInput ? urlInput.value.trim() : '';

    if (!url) {
        showMonitorError('Por favor, insira o link do seu perfil (ex: https://www.kwai.com/@usuario).');
        return;
    }

    const btn = document.getElementById('monitor-start-btn');
    const refreshBtn = document.getElementById('monitor-refresh-btn');
    const errorBox = document.getElementById('monitor-error');
    const resultsBox = document.getElementById('monitor-results');

    if (errorBox) errorBox.style.display = 'none';
    if (resultsBox) resultsBox.style.display = 'none';

    isMonitoringProfile = true;

    if (btn) {
        btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Analisando...';
        btn.disabled = true;
        btn.style.opacity = '0.7';
    }
    if (refreshBtn) {
        refreshBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i>';
        refreshBtn.disabled = true;
    }

    try {
        const orKey = localStorage.getItem('openrouter_api_key') || localStorage.getItem('api_key_openrouter') || '';
        const grokKey = localStorage.getItem('api_key_grok') || '';

        if (!orKey && !grokKey) {
            throw new Error('Chave de API não configurada. Configure nas Configurações (OpenRouter ou Grok).');
        }

        // Show source URL
        const sourceUrlSpan = document.getElementById('monitor-source-url');
        if (sourceUrlSpan) sourceUrlSpan.textContent = url;

        const requestBody = {
            prompt_type: 'monitorar-perfil',
            input_text: `URL para analisar: ${url}`,
            engine: orKey ? 'openrouter' : 'grok',
            api_key_or: orKey,
            api_key_grok: grokKey
        };

        const res = await fetch('https://api.apolloedit.com/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.error || errData.message || 'Falha na comunicação com o servidor de IA.');
        }

        const data = await res.json();

        // The backend returns { status: 'success', data: {...} } for monitorar-perfil
        if (data.status === 'success' && data.data) {
            currentMonitorData = data.data;
            renderMonitorData();
            if (resultsBox) resultsBox.style.display = 'flex';
        } else if (data.texto) {
            // Fallback: try to parse JSON from texto
            try {
                const cleanText = data.texto.replace(/```json/g, '').replace(/```/g, '').trim();
                currentMonitorData = JSON.parse(cleanText);
                renderMonitorData();
                if (resultsBox) resultsBox.style.display = 'flex';
            } catch (e) {
                throw new Error('A IA não retornou dados estruturados. Tente novamente ou verifique a URL.');
            }
        } else {
            throw new Error(data.error || 'Erro desconhecido ao processar dados da página.');
        }

    } catch (err) {
        console.error('handleStartMonitoring error:', err);
        showMonitorError(err.message || 'Erro ao analisar a página. Verifique a URL e tente novamente.');
    } finally {
        isMonitoringProfile = false;

        if (btn) {
            btn.innerHTML = '<i class="fas fa-play"></i> Analisar Perfil';
            btn.disabled = false;
            btn.style.opacity = '1';
        }
        if (refreshBtn) {
            refreshBtn.style.display = 'flex';
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Atualizar Dados';
            refreshBtn.disabled = false;
        }
    }
}

function showMonitorError(msg) {
    const errorBox = document.getElementById('monitor-error');
    const errorMsg = document.getElementById('monitor-error-msg');
    if (errorBox && errorMsg) {
        errorMsg.textContent = msg;
        errorBox.style.display = 'flex';
    } else {
        alert(msg);
    }
}

function formatMonitorNumber(num) {
    if (num === undefined || num === null || num === '') return 'N/A';
    return num.toString().toUpperCase();
}

function renderMonitorData() {
    if (!currentMonitorData) return;

    // Stats
    const followersEl = document.getElementById('monitor-followers');
    const likesEl = document.getElementById('monitor-likes');
    const videosEl = document.getElementById('monitor-videos-count');

    if (followersEl) followersEl.textContent = formatMonitorNumber(currentMonitorData.followers);
    if (likesEl) likesEl.textContent = formatMonitorNumber(currentMonitorData.likes);
    if (videosEl) videosEl.textContent = formatMonitorNumber(currentMonitorData.videos);

    // Recent videos
    const countEl = document.getElementById('monitor-recent-count');
    const grid = document.getElementById('monitor-videos-grid');
    const emptyVideos = document.getElementById('monitor-empty-videos');
    const showAllBtn = document.getElementById('monitor-show-all-btn');

    const videos = currentMonitorData.recentVideos || [];

    if (countEl) countEl.textContent = `${videos.length} encontrados`;

    if (grid) {
        grid.innerHTML = '';

        if (videos.length === 0) {
            if (emptyVideos) emptyVideos.style.display = 'flex';
        } else {
            if (emptyVideos) emptyVideos.style.display = 'none';
            if (showAllBtn && videos.length > 15) showAllBtn.style.display = 'flex';

            const displayVideos = videos.slice(0, 15);
            displayVideos.forEach(v => {
                const card = document.createElement('div');
                card.style.cssText = 'background: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; gap: 10px; transition: box-shadow 0.2s;';

                card.onmouseover = () => card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                card.onmouseout = () => card.style.boxShadow = 'none';

                card.innerHTML = `
                    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;">
                        <h4 style="font-size: 14px; font-weight: 600; color: #fff; margin: 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; flex: 1;" title="${v.title || ''}">${v.title || 'Sem título'}</h4>
                        <div style="background: #ede9fe; color: #8b5cf6; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            <i class="fas fa-play" style="font-size: 12px; margin-left: 2px;"></i>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; padding-top: 8px; border-top: 1px solid #333;">
                        <div style="display: flex; align-items: center; gap: 12px; font-size: 13px; font-weight: 600;">
                            <span style="display: flex; align-items: center; gap: 4px; color: #059669;">
                                <i class="fas fa-eye"></i> ${formatMonitorNumber(v.views)}
                            </span>
                            <span style="display: flex; align-items: center; gap: 4px; color: #db2777;">
                                <i class="fas fa-heart"></i> ${formatMonitorNumber(v.likes)}
                            </span>
                        </div>
                        ${v.date ? `<span style="font-size: 11px; color: #6b7280;">${v.date}</span>` : ''}
                    </div>
                `;

                grid.appendChild(card);
            });
        }
    }
}

function openAllVideosModal() {
    if (!currentMonitorData || !currentMonitorData.recentVideos) return;
    
    const modal = document.getElementById('monitor-all-videos-modal');
    const grid = document.getElementById('monitor-all-videos-grid');
    const subtitle = document.getElementById('monitor-modal-subtitle');
    
    if (!modal || !grid) return;
    
    grid.innerHTML = '';
    subtitle.innerText = `${currentMonitorData.recentVideos.length} v�deos extra�dos do perfil`;
    
    currentMonitorData.recentVideos.forEach(v => {
        const card = document.createElement('div');
        card.style.background = '#1e1e1e';
        card.style.borderRadius = '12px';
        card.style.overflow = 'hidden';
        card.style.border = '1px solid #333';
        card.style.display = 'flex';
        card.style.flexDirection = 'column';
        
        card.innerHTML = `
            <div style="aspect-ratio: 16/9; position: relative; background: #2a2a2a;">
                <img src="/api/proxy-image?url=${encodeURIComponent(v.thumbnail)}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='${v.thumbnail}'">
                <span style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; font-size: 11px; padding: 2px 6px; border-radius: 4px;">
                    ${v.duration}
                </span>
            </div>
            <div style="padding: 12px; flex: 1; display: flex; flex-direction: column;">
                <h4 style="font-size: 13px; font-weight: 600; color: #fff; margin: 0 0 8px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis;">
                    ${v.title}
                </h4>
                <div style="margin-top: auto; display: flex; align-items: center; gap: 12px; font-size: 12px; color: #6b7280;">
                    <span title="Visualiza��es"><i class="fas fa-eye"></i> ${v.views}</span>
                    <span title="Publicado"><i class="far fa-clock"></i> ${v.published}</span>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
    
    modal.style.display = 'flex';
}

function closeAllVideosModal() {
    const modal = document.getElementById('monitor-all-videos-modal');
    if (modal) modal.style.display = 'none';
}
