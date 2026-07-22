// radar_logic.js - Lógica para o Radar YouTube

const RADAR_CATEGORIES = [
    { id: 'politica', label: 'Política Nacional', query: 'notícias política brasil hoje' },
    { id: 'economia', label: 'Economia', query: 'notícias economia brasil mercado' },
    { id: 'mundo', label: 'Internacional', query: 'notícias internacionais hoje' },
    { id: 'polemicas', label: 'Polêmicas e Debates', query: 'debate polêmica podcast brasil' }
];

let activeRadarCategory = RADAR_CATEGORIES[0];
let radarVideos = [];
let isFetchingRadar = false;

document.addEventListener('DOMContentLoaded', () => {
    renderRadarCategories();
    // Fetch inicial na aba de radar (pode ter um pequeno atraso)
    setTimeout(() => fetchRadarVideos(activeRadarCategory), 500);
});

function renderRadarCategories() {
    const container = document.getElementById('radar-categories-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    RADAR_CATEGORIES.forEach(cat => {
        const btn = document.createElement('button');
        
        let cssText = '';
        
        if (activeRadarCategory.id === cat.id) {
            cssText += 'background: #8b5cf6; color: white; box-shadow: 0 1px 2px rgba(0,0,0,0.05);';
        } else {
            cssText += 'background: rgba(0,0,0,0.3); color: #cbd5e1;';
            btn.onmouseover = () => btn.style.backgroundColor = 'rgba(255,255,255,0.1)';
            btn.onmouseout = () => btn.style.backgroundColor = 'rgba(0,0,0,0.3)';
        }
        
        btn.style.cssText = `padding: 8px 16px; border-radius: 9999px; font-size: 14px; font-weight: 500; border: none; cursor: pointer; transition: all 0.2s; ${cssText}`;
        btn.textContent = cat.label;
        
        btn.onclick = () => {
            if (activeRadarCategory.id === cat.id) return;
            activeRadarCategory = cat;
            renderRadarCategories();
            fetchRadarVideos(cat);
        };
        
        container.appendChild(btn);
    });
}

function formatViews(views) {
    if (!views) return '0';
    const v = parseInt(views);
    if (isNaN(v)) return views;
    if (v >= 1000000) return (v / 1000000).toFixed(1) + 'M';
    if (v >= 1000) return (v / 1000).toFixed(1) + 'K';
    return v.toString();
}

async function fetchRadarVideos(categoryObj = activeRadarCategory) {
    if (isFetchingRadar) return;
    
    isFetchingRadar = true;
    radarVideos = [];
    
    const grid = document.getElementById('radar-grid');
    const loading = document.getElementById('radar-loading');
    const errorBox = document.getElementById('radar-error');
    const errorText = document.getElementById('radar-error-text');
    const emptyBox = document.getElementById('radar-empty');
    
    grid.innerHTML = '';
    errorBox.style.display = 'none';
    emptyBox.style.display = 'none';
    loading.style.display = 'flex';
    
    try {
        const res = await fetch(`/api/search-youtube?q=${encodeURIComponent(categoryObj.query)}`);
        if (!res.ok) throw new Error('Falha ao buscar vídeos');
        const data = await res.json();
        
        radarVideos = data.videos || [];
        
        if (radarVideos.length === 0) {
            emptyBox.style.display = 'block';
        } else {
            renderRadarGrid();
        }
        
    } catch (err) {
        console.error(err);
        errorText.textContent = err.message || 'Não foi possível carregar os vídeos em alta no momento.';
        errorBox.style.display = 'block';
    } finally {
        isFetchingRadar = false;
        loading.style.display = 'none';
    }
}

function renderRadarGrid() {
    const grid = document.getElementById('radar-grid');
    grid.innerHTML = '';
    
    radarVideos.forEach(video => {
        const card = document.createElement('div');
        
        // Mantendo o violeta no lugar de indigo para os botões do radar
        card.style.cssText = 'background: #1e1e1e; border-radius: 12px; border: 1px solid #333; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 4px 8px rgba(0,0,0,0.3);';
        
        card.onmouseover = () => {
            card.style.transform = 'translateY(-2px)';
            card.style.boxShadow = '0 6px 12px rgba(0,0,0,0.4)';
        };
        card.onmouseout = () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
        };
        
        card.innerHTML = `
            <div style="position: relative; width: 100%; padding-bottom: 56.25%; cursor: pointer;" onclick="playRadarVideo('${video.url}')">
                <img src="${video.thumbnail}" alt="${video.title}" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;" />
                <div style="position: absolute; inset: 0; background: rgba(0,0,0,0.2); transition: background 0.2s;" onmouseover="this.style.background='rgba(0,0,0,0.1)'" onmouseout="this.style.background='rgba(0,0,0,0.2)'"></div>
                
                <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0'">
                    <div style="width: 48px; height: 48px; background: rgba(139, 92, 246, 0.9); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white;">
                        <i class="fas fa-play" style="margin-left: 4px;"></i>
                    </div>
                </div>
                
                <span style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.8); color: white; font-size: 12px; font-weight: 500; padding: 2px 6px; border-radius: 4px;">
                    ${video.duration}
                </span>
            </div>
            
            <div style="padding: 16px; display: flex; flex-direction: column; flex: 1;">
                <h3 style="font-size: 16px; font-weight: 700; color: #fff; margin: 0 0 8px 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${video.title}">
                    ${video.title}
                </h3>
                
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #2a2a2a; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #64748b; overflow: hidden;">
                        ${video.channelLogo ? `<img src="${video.channelLogo}" style="width:100%;height:100%;object-fit:cover;" />` : `<i class="fas fa-user"></i>`}
                    </div>
                    <span style="font-size: 14px; font-weight: 500; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${video.channel}">
                        ${video.channel}
                    </span>
                </div>
                
                <div style="display: flex; items-center; justify-content: space-between; margin-top: auto; padding-top: 12px; border-top: 1px solid #333; font-size: 12px; color: #64748b;">
                    <div style="display: flex; gap: 12px;">
                        <span style="display: flex; items-center; gap: 4px;">
                            <i class="fas fa-eye"></i> ${formatViews(video.views)}
                        </span>
                        <span style="display: flex; items-center; gap: 4px;">
                            <i class="far fa-clock"></i> ${video.publishedAt}
                        </span>
                    </div>
                </div>
                
                <button onclick="sendRadarToScripts('${encodeURIComponent(video.title)}', '${encodeURIComponent(video.url)}')" style="margin-top: 12px; width: 100%; padding: 8px; background: #ede9fe; color: #8b5cf6; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; transition: background 0.2s;" title="Criar roteiro inspirado neste vídeo" onmouseover="this.style.background='#ddd6fe'" onmouseout="this.style.background='#ede9fe'">
                    <i class="fas fa-pen" style="margin-right: 4px;"></i> Copiar Ideia
                </button>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

function playRadarVideo(url) {
    let videoId = '';
    
    // Extract video ID from YouTube URL
    if (url.includes('youtube.com/watch?v=')) {
        videoId = url.split('v=')[1].split('&')[0];
    } else if (url.includes('youtu.be/')) {
        videoId = url.split('youtu.be/')[1].split('?')[0];
    }
    
    if (!videoId) {
        window.open(url, '_blank');
        return;
    }
    
    const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    const modal = document.getElementById('radar-player-modal');
    const iframe = document.getElementById('radar-player-iframe');
    
    if (modal && iframe) {
        iframe.src = embedUrl;
        modal.style.display = 'flex';
        
        // Prevent body scrolling
        document.body.style.overflow = 'hidden';
    }
}

function closeRadarPlayer() {
    const modal = document.getElementById('radar-player-modal');
    const iframe = document.getElementById('radar-player-iframe');
    
    if (modal && iframe) {
        iframe.src = '';
        modal.style.display = 'none';
        
        // Restore body scrolling
        document.body.style.overflow = 'auto';
    }
}

function sendRadarToScripts(encTitle, encUrl) {
    const title = decodeURIComponent(encTitle);
    const url = decodeURIComponent(encUrl);
    
    localStorage.setItem('scripts_prefill', JSON.stringify({
        text: `Vídeo de referência: ${url}\nTítulo: ${title}\n\nAnalise o assunto deste vídeo e crie um roteiro melhorado com um ângulo diferente.`
    }));
    window.location.href = 'noticias_scripts.html';
}
