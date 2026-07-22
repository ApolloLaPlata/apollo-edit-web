// channel_logic.js - Lógica para a aba Meu Canal

let channelSavedVideos = [];
let isAnalyzingChannel = false;

document.addEventListener('DOMContentLoaded', () => {
    loadSavedVideos();
});

function loadSavedVideos() {
    try {
        channelSavedVideos = JSON.parse(localStorage.getItem('saved_videos') || '[]');
    } catch (e) {
        channelSavedVideos = [];
    }
    renderChannelVideos();
}

function renderChannelVideos() {
    const countSpan = document.getElementById('saved-videos-count');
    const emptyState = document.getElementById('channel-empty-state');
    const grid = document.getElementById('saved-videos-grid');
    const analyzeBtn = document.getElementById('btn-analyze-channel');

    if (countSpan) countSpan.textContent = channelSavedVideos.length;

    if (channelSavedVideos.length === 0) {
        if (emptyState) emptyState.style.display = 'flex';
        if (grid) grid.style.display = 'none';
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.style.opacity = '0.5';
            analyzeBtn.style.cursor = 'not-allowed';
        }
    } else {
        if (emptyState) emptyState.style.display = 'none';
        if (grid) {
            grid.style.display = 'grid';
            grid.innerHTML = '';

            channelSavedVideos.forEach((video, index) => {
                const card = document.createElement('div');
                card.style.cssText = 'background: #1e1e1e; border-radius: 12px; border: 1px solid #333; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 8px rgba(0,0,0,0.3);';

                card.onmouseover = () => {
                    card.style.transform = 'translateY(-2px)';
                    card.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)';
                };
                card.onmouseout = () => {
                    card.style.transform = 'translateY(0)';
                    card.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
                };

                const thumb = video.thumbnail || video.imageUrl || '';
                const title = video.title || 'Sem título';
                const channel = video.channel || video.source || '';
                const views = video.views || '';
                const duration = video.duration || '';

                card.innerHTML = `
                    <div style="position: relative; width: 100%; padding-bottom: 56.25%; background: #2a2a2a;">
                        ${thumb ? `<img src="${thumb}" alt="${title}" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'"/>` : `<div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;"><i class="fab fa-youtube" style="font-size: 48px; color: #dc2626; opacity: 0.4;"></i></div>`}
                        ${duration ? `<span style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; font-size: 12px; font-weight: 500; padding: 2px 6px; border-radius: 4px;"><i class="far fa-clock"></i> ${duration}</span>` : ''}
                    </div>

                    <div style="padding: 16px; display: flex; flex-direction: column; flex: 1;">
                        <h3 style="font-size: 15px; font-weight: 700; color: #fff; margin: 0 0 8px 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${title}">
                            ${title}
                        </h3>

                        ${channel ? `<div style="font-size: 13px; font-weight: 500; color: #94a3b8; margin-bottom: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${channel}"><i class="fas fa-user" style="font-size: 11px; margin-right: 4px;"></i>${channel}</div>` : ''}

                        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: auto; padding-top: 12px; border-top: 1px solid #333; font-size: 12px; color: #64748b;">
                            <span style="display: flex; align-items: center; gap: 4px;">
                                <i class="fas fa-eye"></i> ${views || 'N/A'}
                            </span>
                            <button onclick="removeChannelVideo(${index})" style="background: none; border: none; color: #ef4444; cursor: pointer; padding: 4px; border-radius: 4px; font-size: 14px;" title="Remover" onmouseover="this.style.background='#fee2e2'" onmouseout="this.style.background='transparent'">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;

                grid.appendChild(card);
            });
        }

        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.style.opacity = '1';
            analyzeBtn.style.cursor = 'pointer';
        }
    }
}

function removeChannelVideo(index) {
    channelSavedVideos.splice(index, 1);
    localStorage.setItem('saved_videos', JSON.stringify(channelSavedVideos));
    renderChannelVideos();
}

async function analyzeChannel() {
    if (isAnalyzingChannel || channelSavedVideos.length === 0) return;

    const btn = document.getElementById('btn-analyze-channel');
    const resultBox = document.getElementById('channel-analysis-result');
    const resultContent = document.getElementById('channel-analysis-content');

    isAnalyzingChannel = true;

    if (btn) {
        btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Analisando...';
        btn.disabled = true;
        btn.style.opacity = '0.7';
    }

    if (resultBox) resultBox.style.display = 'none';

    try {
        const orKey = localStorage.getItem('openrouter_api_key') || localStorage.getItem('api_key_openrouter') || '';
        const grokKey = localStorage.getItem('api_key_grok') || '';

        if (!orKey && !grokKey) {
            throw new Error('Chave de API não configurada. Configure nas Configurações (OpenRouter ou Grok).');
        }

        // Build a text summary of the saved videos for input_text
        const videosText = channelSavedVideos.map(v =>
            `- ${v.title || 'Sem título'} (Canal: ${v.channel || v.source || 'N/A'}, Visualizações: ${v.views || 'N/A'})`
        ).join('\n');

        const requestBody = {
            prompt_type: 'analisar-canal',
            input_text: videosText,
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
            throw new Error(errData.error || errData.message || 'Falha na comunicação com o servidor AI.');
        }

        const data = await res.json();
        const texto = data.texto || data.content || 'Análise falhou.';

        if (resultBox && resultContent) {
            resultBox.style.display = 'block';
            // Render markdown if marked is available
            if (typeof marked !== 'undefined' && marked.parse) {
                resultContent.innerHTML = marked.parse(texto);
            } else {
                resultContent.innerHTML = texto.replace(/\n/g, '<br>');
            }
        }

    } catch (err) {
        console.error('analyzeChannel error:', err);
        if (typeof showToast === 'function') {
            showToast('Erro ao analisar canal: ' + err.message, 'error');
        } else {
            alert('Erro ao analisar canal: ' + err.message);
        }
    } finally {
        isAnalyzingChannel = false;

        if (btn) {
            btn.innerHTML = '<i class="fas fa-bullseye"></i> Analisar Canal & Sugerir Temas';
            btn.disabled = false;
            btn.style.opacity = '1';
        }
    }
}
