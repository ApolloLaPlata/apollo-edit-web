// miner_logic.js - Lógica para a Aba de Mineração de Vídeos YouTube

let minerState = {
    topic: '',
    isFetching: false,
    videos: [],
    error: null,
    analyzingId: null
};

function formatCount(n) {
    if (!n && n !== 0) return '—';
    const num = typeof n === 'string' ? parseInt(n.replace(/[^0-9]/g, '')) : n;
    if (isNaN(num)) return n;
    if (num >= 1000000) return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    return num.toString();
}

function formatDuration(dur) {
    if (!dur) return '';
    // Handle ISO 8601 (PT#M#S) or already formatted
    const match = dur.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
    if (match) {
        const h = parseInt(match[1] || 0);
        const m = parseInt(match[2] || 0);
        const s = parseInt(match[3] || 0);
        if (h > 0) return `${h}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
        return `${m}:${String(s).padStart(2,'0')}`;
    }
    return dur;
}

function getSavedVideos() {
    try {
        return JSON.parse(localStorage.getItem('saved_videos') || '[]');
    } catch(e) { return []; }
}

function setSavedVideos(arr) {
    localStorage.setItem('saved_videos', JSON.stringify(arr));
}

function isVideoSaved(videoId) {
    return getSavedVideos().some(v => v.id === videoId || v.videoId === videoId);
}

function toggleSaveVideo(video) {
    let saved = getSavedVideos();
    const id = video.id || video.videoId;
    if (saved.some(v => (v.id || v.videoId) === id)) {
        saved = saved.filter(v => (v.id || v.videoId) !== id);
        showToast('Vídeo removido dos favoritos', 'info');
    } else {
        saved.push(video);
        showToast('⭐ Vídeo salvo nos favoritos!', 'success');
    }
    setSavedVideos(saved);
    renderMinerGrid();
}

document.addEventListener('DOMContentLoaded', () => {
    initMinerTab();
});

function initMinerTab() {
    const topicInput = document.getElementById('miner-topic-input');
    if (topicInput) {
        topicInput.addEventListener('input', (e) => {
            minerState.topic = e.target.value;
            updateMinerButtons();
        });
        topicInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') minerSearch();
        });
    }

    const searchBtn = document.getElementById('miner-search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', minerSearch);
    }

    updateMinerButtons();
    renderMinerGrid();
}

function updateMinerButtons() {
    const btn = document.getElementById('miner-search-btn');
    const hasTopic = minerState.topic.trim().length > 0;
    if (btn) {
        btn.disabled = minerState.isFetching || !hasTopic;
        btn.style.opacity = btn.disabled ? '0.5' : '1';
        btn.style.cursor = btn.disabled ? 'not-allowed' : 'pointer';
        if (minerState.isFetching) {
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Minerando...';
        } else {
            btn.innerHTML = '<i class="fas fa-search"></i> Minerar Vídeos';
        }
    }
}

function minerSetError(msg) {
    minerState.error = msg;
    const errorEl = document.getElementById('miner-error');
    const textEl = document.getElementById('miner-error-text');
    if (errorEl && textEl) {
        if (msg) {
            textEl.textContent = msg;
            errorEl.style.display = 'flex';
        } else {
            errorEl.style.display = 'none';
        }
    }
}

async function minerSearch() {
    if (!minerState.topic.trim()) {
        minerSetError('Por favor, digite um tema para buscar.');
        return;
    }

    minerSetError(null);
    minerState.isFetching = true;
    minerState.videos = [];
    updateMinerButtons();
    renderMinerGrid();

    try {
        const response = await fetch(`/api/search-youtube?q=${encodeURIComponent(minerState.topic)}`);
        if (!response.ok) throw new Error(`Erro: ${response.status}`);

        const data = await response.json();
        minerState.videos = data.videos || [];

        if (minerState.videos.length === 0) {
            minerSetError('Nenhum vídeo encontrado para este tema.');
        }
    } catch (err) {
        minerSetError('Erro ao buscar vídeos: ' + err.message);
    } finally {
        minerState.isFetching = false;
        updateMinerButtons();
        renderMinerGrid();
    }
}

function renderMinerGrid() {
    const grid = document.getElementById('miner-grid');
    const loading = document.getElementById('miner-loading');
    const empty = document.getElementById('miner-empty');

    if (minerState.isFetching) {
        if (loading) loading.style.display = 'flex';
        if (empty) empty.style.display = 'none';
        if (grid) grid.style.display = 'none';
        return;
    }

    if (loading) loading.style.display = 'none';

    if (minerState.videos.length === 0) {
        if (empty) empty.style.display = 'flex';
        if (grid) grid.style.display = 'none';
        return;
    }

    if (empty) empty.style.display = 'none';
    if (!grid) return;

    grid.style.display = 'grid';
    grid.innerHTML = '';

    minerState.videos.forEach((video, idx) => {
        const id = video.id || video.videoId || idx;
        const saved = isVideoSaved(id);
        const thumbnail = video.thumbnail || video.thumbnails?.high?.url || video.thumbnails?.default?.url || '';
        const title = video.title || 'Sem título';
        const author = video.channelTitle || video.author || 'Desconhecido';
        const views = formatCount(video.viewCount || video.views);
        const duration = formatDuration(video.duration);

        const card = document.createElement('div');
        card.className = 'news-card';
        card.style.cssText = 'padding: 0; overflow: hidden; transition: transform 0.2s;';
        card.onmouseover = () => card.style.transform = 'translateY(-4px)';
        card.onmouseout = () => card.style.transform = 'translateY(0)';

        card.innerHTML = `
            <div style="position: relative; aspect-ratio: 16/9; background: #000; overflow: hidden;">
                <img src="${thumbnail}" style="width:100%; height:100%; object-fit:cover;" onerror="this.style.display='none'">
                ${duration ? `<span style="position:absolute; bottom:8px; right:8px; background:rgba(0,0,0,0.8); color:#fff; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:700; font-family:'Nunito',sans-serif;">${duration}</span>` : ''}
            </div>
            <div style="padding: 16px;">
                <h3 style="font-size:14px; font-weight:700; color:#fff; margin:0 0 8px 0; line-height:1.4; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; font-family:'Nunito',sans-serif;">${title}</h3>
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
                    <span style="font-size:12px; color:#94a3b8; font-family:'Nunito',sans-serif;"><i class="fas fa-user" style="margin-right:4px;"></i>${author}</span>
                    <span style="font-size:12px; color:#94a3b8; font-family:'Nunito',sans-serif;"><i class="fas fa-eye" style="margin-right:4px;"></i>${views}</span>
                </div>
                <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <button onclick='toggleSaveVideo(${JSON.stringify({id, title, author, thumbnail}).replace(/'/g,"&#39;")})' style="flex:1; min-width:0; padding:8px 6px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; font-family:'Nunito',sans-serif; transition:0.2s; background:${saved ? '#FFD32A' : 'rgba(255,211,42,0.15)'}; color:${saved ? '#000' : '#FFD32A'};" title="${saved ? 'Remover favorito' : 'Salvar favorito'}">
                        ⭐ ${saved ? 'Salvo' : 'Salvar'}
                    </button>
                    <button onclick="minerAnalyze(${idx})" id="miner-analyze-${idx}" style="flex:1; min-width:0; padding:8px 6px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; font-family:'Nunito',sans-serif; transition:0.2s; background:rgba(155,89,182,0.15); color:#9B59B6;">
                        🔍 Analisar
                    </button>
                    <button onclick="minerSendToScripts(${idx})" style="flex:1; min-width:0; padding:8px 6px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; font-family:'Nunito',sans-serif; transition:0.2s; background:rgba(46,204,113,0.15); color:#2ECC71;">
                        📝 Roteiro
                    </button>
                    <button onclick="minerSendToHUD(${idx})" style="padding:8px 10px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; font-family:'Nunito',sans-serif; transition:0.2s; background:rgba(52,152,219,0.15); color:#3498DB;" title="Enviar ao HUD">
                        🎒
                    </button>
                </div>
                <div id="miner-analysis-${idx}" style="display:none; margin-top:12px;"></div>
            </div>
        `;
        grid.appendChild(card);
    });
}

async function minerAnalyze(idx) {
    const video = minerState.videos[idx];
    if (!video) return;

    const btn = document.getElementById(`miner-analyze-${idx}`);
    const analysisDiv = document.getElementById(`miner-analysis-${idx}`);

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    if (analysisDiv) {
        analysisDiv.style.display = 'block';
        analysisDiv.innerHTML = '<div style="color:#9B59B6; font-size:13px; padding:8px;"><i class="fas fa-circle-notch fa-spin"></i> Analisando com IA...</div>';
    }

    try {
        const response = await fetch('/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt_type: 'minerar',
                input_text: `Título: ${video.title}\nCanal: ${video.channelTitle || video.author}\nVisualizações: ${video.viewCount || video.views}\nDescrição: ${video.description || ''}`,
                engine: localStorage.getItem('default_engine') || 'gemini',
                api_key_or: localStorage.getItem('openrouter_api_key') || '',
                api_key_grok: localStorage.getItem('api_key_grok') || ''
            })
        });

        if (!response.ok) throw new Error(`Erro: ${response.status}`);
        const data = await response.json();
        const content = data.content || data.text || 'Sem resultado.';

        if (analysisDiv) {
            analysisDiv.innerHTML = `
                <div style="background:rgba(155,89,182,0.1); border:1px solid rgba(155,89,182,0.3); border-radius:8px; padding:12px; font-size:13px; color:#cbd5e1; line-height:1.6; font-family:'Nunito',sans-serif;">
                    <strong style="color:#9B59B6;"><i class="fas fa-brain"></i> Análise IA:</strong><br><br>
                    ${content.replace(/\n/g, '<br>')}
                </div>
            `;
        }
    } catch (err) {
        if (analysisDiv) {
            analysisDiv.innerHTML = `<div style="color:#E74C3C; font-size:12px; padding:8px;"><i class="fas fa-exclamation-triangle"></i> Falha: ${err.message}</div>`;
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '🔍 Analisar';
        }
    }
}

function minerSendToScripts(idx) {
    const video = minerState.videos[idx];
    if (!video) return;
    localStorage.setItem('scripts_prefill', JSON.stringify({
        text: video.title
    }));
    window.location.href = 'noticias_scripts.html';
}

function minerSendToHUD(idx) {
    const video = minerState.videos[idx];
    if (!video) return;
    const thumbnail = video.thumbnail || video.thumbnails?.high?.url || '';
    if (typeof window.addToTransferArea === 'function') {
        window.addToTransferArea('video', video.title, video.channelTitle || video.author || '', thumbnail);
        showToast('🎒 Vídeo adicionado ao HUD!', 'success');
    } else {
        showToast('HUD não disponível', 'error');
    }
}
