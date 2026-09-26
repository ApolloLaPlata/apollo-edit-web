// State para a tab Caçador de Notícias
let newsState = {
    topic: '',
    newsCount: 5,
    isFetching: false,
    items: [],
    error: null
};

const PREDEFINED_TOPICS = [
    "Política Nacional", "Bastidores de Brasília", "Supremo Tribunal Federal", 
    "Congresso Nacional", "Economia do Brasil", "Eleições", "Direita no Brasil", 
    "Geopolítica", "Liberdade de Expressão"
];

function initNewsTab() {
    console.log("Inicializando tab-news");
    
    const topicInput = document.getElementById('news-topic-input');
    if (topicInput) {
        topicInput.addEventListener('input', (e) => {
            newsState.topic = e.target.value;
            updateNewsButtons();
        });
    }

    const countInput = document.getElementById('news-count');
    if (countInput) {
        countInput.addEventListener('input', (e) => {
            newsState.newsCount = parseInt(e.target.value) || 5;
        });
    }

    renderPredefinedTopics();
    updateNewsButtons();
    renderNewsOutput();
}

function renderPredefinedTopics() {
    const container = document.getElementById('news-topics-container');
    if (!container) return;

    container.innerHTML = '';
    PREDEFINED_TOPICS.forEach(topic => {
        const isSelected = newsState.topic.includes(topic);
        const btn = document.createElement('button');
        btn.textContent = topic;
        btn.disabled = newsState.isFetching;
        if (isSelected) {
            btn.style.cssText = 'padding: 6px 14px; font-size: 13px; font-weight: 500; border-radius: 9999px; border: 1px solid; cursor: pointer; margin: 0 8px 8px 0; background: rgba(139,92,246,0.2); border-color: #8b5cf6; color: #a78bfa;';
        } else {
            btn.style.cssText = 'padding: 6px 14px; font-size: 13px; font-weight: 500; border-radius: 9999px; border: 1px solid #444; cursor: pointer; margin: 0 8px 8px 0; background: rgba(0,0,0,0.3); color: #cbd5e1;';
            btn.onmouseover = () => btn.style.backgroundColor = 'rgba(255,255,255,0.08)';
            btn.onmouseout = () => btn.style.backgroundColor = 'rgba(0,0,0,0.3)';
        }
        btn.onclick = () => handleTopicClick(topic);
        container.appendChild(btn);
    });
}

function handleTopicClick(topic) {
    let currentTopic = newsState.topic.trim();
    if (currentTopic.includes(topic)) {
        currentTopic = currentTopic.replace(new RegExp(`(^|,\s*)${topic}(,\s*|$)`, 'g'), ', ').replace(/^,\s*|,\s*$/g, '');
    } else {
        currentTopic = currentTopic ? `${currentTopic}, ${topic}` : topic;
    }
    newsState.topic = currentTopic;
    const input = document.getElementById('news-topic-input');
    if (input) input.value = newsState.topic;
    renderPredefinedTopics();
    updateNewsButtons();
}

function updateNewsButtons() {
    const fetchBtn = document.getElementById('news-fetch-btn');
    const hasTopic = newsState.topic.trim().length > 0;
    
    if (fetchBtn) {
        fetchBtn.disabled = newsState.isFetching || !hasTopic;
        fetchBtn.style.opacity = fetchBtn.disabled ? '0.5' : '1';
        fetchBtn.style.cursor = fetchBtn.disabled ? 'not-allowed' : 'pointer';
        
        if (newsState.isFetching) {
            fetchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando Notícias...';
        } else {
            fetchBtn.innerHTML = '<i class="fas fa-search"></i> Buscar Notícias';
        }
    }
}

function newsSetError(msg) {
    newsState.error = msg;
    const errorEl = document.getElementById('news-error');
    const textEl = document.getElementById('news-error-text');
    if (errorEl && textEl) {
        if (msg) {
            textEl.textContent = msg;
            errorEl.style.display = 'flex';
        } else {
            errorEl.style.display = 'none';
        }
    }
}

async function newsFetch() {
    if (!newsState.topic.trim()) {
        newsSetError("Por favor, digite um tema para buscar.");
        return;
    }
    
    newsSetError(null);
    newsState.isFetching = true;
    newsState.items = [];
    updateNewsUI();

    try {
        const response = await fetch('/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt_type: 'cacar',
                input_text: newsState.topic,
                news_count: newsState.newsCount,
                engine: localStorage.getItem('default_engine') || 'gemini',
                api_key_or: localStorage.getItem('openrouter_api_key') || '',
                api_key_grok: localStorage.getItem('api_key_grok') || ''
            })
        });

        if (!response.ok) {
            throw new Error('Falha na resposta do servidor.');
        }

        const data = await response.json();
        
        if (data.status === 'success' || data.success) {
            let parsedItems = data.news || [];
            if (parsedItems.length === 0 && data.content) {
                try {
                    let clean = data.content.replace(/```json/g, '').replace(/```/g, '').trim();
                    parsedItems = JSON.parse(clean);
                } catch(e){}
            }
            newsState.items = parsedItems;
            
            // Buscar imagens ausentes
            const pixabayKey = localStorage.getItem('api_key_pixabay') || '';
            const pexelsKey = localStorage.getItem('api_key_pexels') || '';
            
            for (let i = 0; i < newsState.items.length; i++) {
                const item = newsState.items[i];
                if (!item.imageUrl || item.imageUrl.trim() === "") {
                    try {
                        const query = item.imageSearchQuery || (item.title + " " + item.source);
                        const res = await fetch(`/api/search-images?q=${encodeURIComponent(query)}&pixabay=${pixabayKey}&pexels=${pexelsKey}`);
                        if (res.ok) {
                            const imgData = await res.json();
                            if (imgData.urls && imgData.urls.length > 0) {
                                const firstUrl = imgData.urls[0];
                                item.imageUrl = typeof firstUrl === 'string' ? firstUrl : firstUrl.url;
                            }
                        }
                    } catch (e) {
                        console.error("Failed to fetch image for news:", item.title);
                    }
                }
                updateNewsUI();
            }
        } else {
            throw new Error(data.message || data.error || 'Erro desconhecido');
        }
    } catch (err) {
        newsSetError("Erro ao buscar notícias: " + err.message);
    } finally {
        newsState.isFetching = false;
        updateNewsUI();
    }
}

function updateNewsUI() {
    updateNewsButtons();
    renderPredefinedTopics();
    renderNewsOutput();
}

function newsCopy(idx) {
    const item = newsState.items[idx];
    const text = `Título: ${item.title}\nResumo: ${item.summary}\nFonte: ${item.source}\nLink: ${item.url}`;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Notícia copiada!', 'success');
    });
}

function newsUse(idx) {
    const item = newsState.items[idx];
    const text = `Título: ${item.title}\nResumo: ${item.summary}\nFonte: ${item.source}\nLink: ${item.url}`;
    const input = document.getElementById('script-input');
    if (input) {
        input.value = text;
        const evt = new Event('input');
        input.dispatchEvent(evt);
    }
    showToast('Roteiro preenchido! Redirecionando...', 'success');
    window.location.href = 'noticias_scripts.html';
}

async function newsDeepDive(idx) {
    const item = newsState.items[idx];
    const btn = document.getElementById(`btn-deepdive-${idx}`);
    const resDiv = document.getElementById(`deep-dive-${idx}`);
    
    if (btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    if (resDiv) {
        resDiv.style.display = 'block';
        resDiv.innerHTML = '<div style="color: #64748b; font-size: 13px;">Aprofundando análise jornalística...</div>';
    }

    try {
        const response = await fetch('/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt_type: 'deep-dive',
                input_text: `Título: ${item.title}\nResumo: ${item.summary}\nURL: ${item.url}`,
                engine: localStorage.getItem('default_engine') || 'gemini',
                api_key_or: localStorage.getItem('openrouter_api_key') || '',
                api_key_grok: localStorage.getItem('api_key_grok') || ''
            })
        });

        if (!response.ok) throw new Error('Falha na resposta do servidor.');
        
        const data = await response.json();
        if (data.success || data.status === 'success') {
            const content = data.content || '';
            // Basic markdown parsing for bold and line breaks
            let parsed = content.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>').replace(/\\*(.*?)\\*/g, '<em>$1</em>').replace(/#(.*?)<br>/g, '<strong>$1</strong><br>');
            if (resDiv) {
                resDiv.innerHTML = `<div style="font-size: 13px; color: #cbd5e1; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; margin-top: 12px; border-left: 4px solid #8b5cf6;"><strong><i class="fas fa-search-plus" style="color:#8b5cf6"></i> Análise Profunda:</strong><br><br>${parsed}</div>`;
            }
        // Dispara Webhook se configurado
            const webhookUrl = localStorage.getItem('webhook_url_deepdive');
            if (webhookUrl && item) {
                try {
                    fetch(webhookUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            title: item.title,
                            summary: item.summary,
                            url: item.url,
                            deepdive_text: data.content || '',
                            timestamp: new Date().toISOString()
                        })
                    }).catch(() => {}); // fire and forget
                } catch(e) {}
            }
        } else {
            throw new Error(data.error || 'Erro desconhecido');
        }
    } catch (err) {
        if (resDiv) {
            resDiv.innerHTML = `<div style="color: red; font-size: 12px;">Erro: ${err.message}</div>`;
        }
    } finally {
        if (btn) btn.innerHTML = '<i class="fas fa-search-plus"></i>';
    }
}

function renderNewsOutput() {
    const emptyState = document.getElementById('news-empty-state');
    const loadingState = document.getElementById('news-loading-state');
    const container = document.getElementById('news-assets-container');
    
    if (newsState.isFetching && newsState.items.length === 0) {
        if (emptyState) emptyState.style.display = 'none';
        if (container) container.style.display = 'none';
        if (loadingState) loadingState.style.display = 'flex';
        return;
    }
    
    if (newsState.items.length === 0) {
        if (loadingState) loadingState.style.display = 'none';
        if (container) container.style.display = 'none';
        if (emptyState) emptyState.style.display = 'flex';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    if (loadingState) loadingState.style.display = 'none';
    if (container) {
        container.style.display = 'flex';
        container.innerHTML = '';
        
        newsState.items.forEach((item, idx) => {
            let html = `
                <div style="background: #1e1e1e; border-radius: 12px; border: 1px solid #333; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.3); transition: transform 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.3)'">
                    ${item.imageUrl ? `
                        <div style="aspect-ratio: 16/9; background: #2a2a2a; position: relative; overflow: hidden;">
                            <img src="/api/proxy-image?url=${encodeURIComponent(item.imageUrl)}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='${item.imageUrl}'">
                        </div>
                    ` : ''}
                    <div style="padding: 16px;">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                            <span style="font-size: 12px; font-weight: 600; padding: 4px 8px; border-radius: 4px; background: rgba(0,0,0,0.3); color: #94a3b8; text-transform: uppercase;">
                                ${item.source}
                            </span>
                            <span style="font-size: 12px; color: #64748b;">${item.date}</span>
                        </div>
                        <h3 style="font-size: 16px; font-weight: 700; margin: 0 0 8px 0; color: #fff; line-height: 1.4;">
                            <a href="${item.url}" target="_blank" style="color: inherit; text-decoration: none;" onmouseover="this.style.color='#ea580c'" onmouseout="this.style.color='inherit'">${item.title}</a>
                        </h3>
                        <p style="font-size: 14px; color: #94a3b8; margin: 0 0 16px 0; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                            ${item.summary}
                        </p>
                        <div style="display: flex; gap: 8px;">
                            <button onclick="newsUse(${idx})" style="flex: 1; background: #ea580c; color: white; border: none; padding: 8px; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; display: flex; align-items: center; justify-content: center; gap: 4px;" onmouseover="this.style.background='#c2410c'" onmouseout="this.style.background='#ea580c'">
                                <i class="fas fa-pen-tool"></i> Usar
                            </button>
                            <button id="btn-deepdive-${idx}" onclick="newsDeepDive(${idx})" style="padding: 8px 12px; background: #8b5cf6; color: white; border: none; border-radius: 6px; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#7c3aed'" onmouseout="this.style.background='#8b5cf6'" title="Aprofundar Notícia">
                                <i class="fas fa-search-plus"></i>
                            </button>
                            <button onclick="newsCopy(${idx})" style="padding: 8px 12px; background: rgba(0,0,0,0.3); color: #94a3b8; border: none; border-radius: 6px; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(0,0,0,0.3)'" title="Copiar Notícia">
                                <i class="fas fa-copy"></i>
                            </button>
                            <a href="${item.url}" target="_blank" style="padding: 8px 12px; background: rgba(0,0,0,0.3); color: #94a3b8; border: none; border-radius: 6px; cursor: pointer; transition: background 0.2s; text-decoration: none; display: flex; align-items: center;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(0,0,0,0.3)'" title="Ler original">
                                <i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                        <div id="deep-dive-${idx}" style="display: none;"></div>
                    </div>
                </div>
            `;
            container.innerHTML += html;
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initNewsTab();
});
