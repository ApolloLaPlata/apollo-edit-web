// ------------------------------------------------------------------
// APOLLO TIMELINE EDITOR - CORE ENGINE
// ------------------------------------------------------------------

// --- 1. ESTADO GLOBAL ---
const State = {
    zoomLevel: 50,
    currentTime: 0,
    clips: [],
    transitions: [], // {id, leftClipId, rightClipId, type, duration, element}
    nextId: 1,
    activeTool: 'select',
    projectRatio: 'auto'
};

// --- 2. CONFIGURAÇÃO DE UI ---
const UI = {
    zoomSlider: document.getElementById('zoom-slider'),
    playhead: document.getElementById('playhead'),
    timeDisplay: document.getElementById('current-time-display'),
    trackV1: document.getElementById('track-v1-content'),
    trackA1: document.getElementById('track-a1-content'),
    mediaItems: document.querySelectorAll('.media-item')
};

// --- 3. INICIALIZAÇÃO DE DRAG AND DROP (Da Biblioteca para a Timeline) ---
UI.mediaItems.forEach(item => {
    item.addEventListener('dragstart', (e) => {
        // Usa dataset.path se disponível (item importado), senão pega o texto do media-info
        const path = item.dataset.path || 
                     item.querySelector('.media-info')?.firstChild?.textContent?.trim() ||
                     item.querySelector('.media-info')?.textContent?.trim() || 'media';
        e.dataTransfer.setData('text/plain', JSON.stringify({
            type: item.dataset.type,
            duration: parseFloat(item.dataset.duration) || 5.0,
            name: path,
            color: item.dataset.type === 'video' ? '#3b82f6' : '#f97316'
        }));
        e.dataTransfer.effectAllowed = 'copy';
    });
});

// Configurar as zonas de drop (Os trilhos) — gerenciado pela função setupDropZone() mais abaixo.
// As trilhas V1 e A1 recebem o setup após a definição da função no Passo 10.

// =============================================================
// === PASSO 11.5: SAAS TIMELINE BRIDGE SYNC                ===
// =============================================================

function syncAssetsFromHub() {
    try {
        let saved = localStorage.getItem('apollo_timeline_assets');
        if(saved) {
            let assets = JSON.parse(saved);
            const grid = document.getElementById('media-grid');
            if(!grid) return;
            
            // clear if we are injecting fresh
            assets.forEach(asset => {
                // Check if already in grid
                if(document.querySelector(`[data-path="${asset.name}"]`)) return;
                
                const div = document.createElement('div');
                div.className = 'media-item';
                div.draggable = true;
                div.dataset.type = asset.type;
                div.dataset.duration = '5.0'; // Default
                div.dataset.path = asset.name;
                
                div.innerHTML = `
                    <div class="media-icon">${asset.type === 'video' ? '🎬' : '🖼️'}</div>
                    <div class="media-info" title="${asset.name}">
                        <div>${asset.name}</div>
                        <small style="color:#aaa;">5.0s</small>
                    </div>
                `;
                
                div.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', JSON.stringify({
                        type: asset.type,
                        duration: 5.0,
                        name: asset.name,
                        color: asset.type === 'video' ? '#3b82f6' : '#f97316'
                    }));
                    e.dataTransfer.effectAllowed = 'copy';
                });
                
                grid.appendChild(div);
            });
        }
    } catch(e) {
        console.error("Erro ao sincronizar assets da bridge:", e);
    }
}

// Call once on load, and listen to storage events
window.addEventListener('load', syncAssetsFromHub);
window.addEventListener('storage', syncAssetsFromHub);

// =============================================================
// === PASSO 12: FERRAMENTA GILETE (RAZOR TOOL)             ===
// =============================================================

// Linha de preview de corte (DOM)
let razorLine = null;

function getRazorLine() {
    if (!razorLine) {
        razorLine = document.createElement('div');
        razorLine.id = 'razor-line';
        razorLine.style.cssText = `
            position: absolute; top: 0; bottom: 0; width: 2px;
            background: #ef4444; pointer-events: none; z-index: 200;
            display: none;
        `;
        // Adicionar um cabeçalho
        const head = document.createElement('div');
        head.style.cssText = `
            position: absolute; top: -18px; left: -12px;
            background: #ef4444; color: white; font-size: 0.65rem;
            padding: 2px 4px; border-radius: 3px; white-space: nowrap;
        `;
        head.id = 'razor-line-label';
        razorLine.appendChild(head);
        document.getElementById('timeline-tracks').appendChild(razorLine);
    }
    return razorLine;
}

// Função central de corte — usada pela tecla C e pelo clique no modo Gilete
function splitClipAtTime(clip, cutTime) {
    if (cutTime <= clip.start + 0.05 || cutTime >= clip.start + clip.duration - 0.05) return null; // Corte muito na borda

    const leftDuration = cutTime - clip.start;
    const rightTrimIn = (clip.trimIn || 0) + leftDuration;
    const rightDuration = clip.duration - leftDuration;
    const trackEl = clip.element.parentElement;

    // Reduz o clipe esquerdo
    clip.duration = leftDuration;
    updateClipVisual(clip, clip.element);

    // Cria o clipe direito
    const newClip = createClip(
        clip.name,
        clip.type,
        cutTime,
        rightDuration,
        clip.color,
        trackEl,
        rightTrimIn
    );
    return newClip;
}

// Dividir TODOS os clipes sob o playhead (modo tecla C global)
function splitAllClipsAtPlayhead() {
    const cutTime = State.currentTime;
    const clipsToSplit = State.clips.filter(
        c => cutTime > c.start + 0.05 && cutTime < c.start + c.duration - 0.05
    );
    clipsToSplit.forEach(c => splitClipAtTime(c, cutTime));
}

// Ativar/desativar a ferramenta
function setActiveTool(tool) {
    State.activeTool = tool;
    document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));

    if (tool === 'razor') {
        document.getElementById('tool-btn-razor').classList.add('active');
        document.getElementById('timeline-tracks').style.cursor = 'url("data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'24\' height=\'24\' viewBox=\'0 0 24 24\'><line x1=\'5\' y1=\'5\' x2=\'19\' y2=\'19\' stroke=\'%23ef4444\' stroke-width=\'2\'/>\<line x1=\'5\' y1=\'19\' x2=\'19\' y2=\'5\' stroke=\'%23ef4444\' stroke-width=\'2\'/></svg>") 12 12, crosshair';
    } else {
        document.getElementById('tool-btn-select').classList.add('active');
        document.getElementById('timeline-tracks').style.cursor = 'default';
        getRazorLine().style.display = 'none';
    }
}

// Hover no modo Gilete — mostrar a linha
function setupRazorHover(trackContent) {
    const onMouseMove = (e) => {
        if (State.activeTool !== 'razor') return;

        const trackEl = trackContent.closest('.track');
        const tracksContainer = document.getElementById('timeline-tracks');
        const containerRect = tracksContainer.getBoundingClientRect();
        const contentRect = trackContent.getBoundingClientRect();

        // Posição X relativa ao container de tracks
        const xInContent = e.clientX - contentRect.left + trackContent.scrollLeft;
        const cutTime = Math.max(0, xInContent / State.zoomLevel);

        // Verificar se o mouse está sobre algum clipe
        const clipUnder = State.clips.find(c =>
            c.element.parentElement === trackContent &&
            cutTime > c.start + 0.05 &&
            cutTime < c.start + c.duration - 0.05
        );

        if (clipUnder) {
            UI.razorLine.style.display = 'block';
            UI.razorLine.style.left = (cutTime * State.zoomLevel) + 'px';
            UI.razorLine.style.top = contentRect.top - containerRect.top + 'px';
            UI.razorLine.style.height = contentRect.height + 'px';
            document.body.style.cursor = 'crosshair';
        } else {
            UI.razorLine.style.display = 'none';
            document.body.style.cursor = 'default';
        }
    };

    const onMouseLeave = () => {
        if (State.activeTool === 'razor') {
            UI.razorLine.style.display = 'none';
            document.body.style.cursor = 'default';
        }
    };

    const onClick = (e) => {
        if (State.activeTool !== 'razor') return;

        const contentRect = trackContent.getBoundingClientRect();
        const xInContent = e.clientX - contentRect.left + trackContent.scrollLeft;
        const cutTime = Math.max(0, xInContent / State.zoomLevel);

        // Clicar fora de qualquer clipe — mover o playhead e cortar tudo
        const clipUnder = State.clips.find(c =>
            c.element.parentElement === trackContent &&
            cutTime > c.start + 0.05 &&
            cutTime < c.start + c.duration - 0.05
        );

        if (clipUnder) {
            const splitResult = splitClipAtTime(clipUnder, cutTime);
            if (splitResult && typeof HistoryManager !== 'undefined') HistoryManager.saveState();
        } else {
            State.currentTime = cutTime;
            updatePlayhead();
            splitAllClipsAtPlayhead();
            if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
        }
    };

    trackContent.addEventListener('mousemove', onMouseMove);
    trackContent.addEventListener('mouseleave', onMouseLeave);
    trackContent.addEventListener('click', onClick);

    trackContent._cleanupRazor = () => {
        trackContent.removeEventListener('mousemove', onMouseMove);
        trackContent.removeEventListener('mouseleave', onMouseLeave);
        trackContent.removeEventListener('click', onClick);
    };
}


// --- 4. ENGINE DE CLIPES ---
function createClip(name, type, startTime, duration, color, trackElement, trimIn = 0.0, width = 0, height = 0) {
    const clip = {
        id: State.nextId++,
        name: name,
        type: type, // 'video' ou 'audio'
        start: startTime, // Onde começa na timeline
        duration: duration,
        trimIn: trimIn, // Onde começa dentro do arquivo original
        color: color,
        element: null,
        width: width,
        height: height
    };

    // Criar DOM Element
    const dom = document.createElement('div');
    dom.className = 'timeline-clip';
    dom.style.position = 'absolute';
    dom.style.height = '60px';
    dom.style.top = '10px';
    dom.style.backgroundColor = color;
    dom.style.borderRadius = '4px';
    dom.style.border = '1px solid rgba(255,255,255,0.3)';
    dom.style.color = '#fff';
    dom.style.fontSize = '0.75rem';
    dom.style.padding = '4px';
    dom.style.overflow = 'hidden';
    dom.style.cursor = 'grab';
    dom.style.boxShadow = '0 4px 6px rgba(0,0,0,0.3)';
    dom.style.userSelect = 'none';
    // Waveform para áudio | Thumbnail para vídeo
    const extraVisual = type === 'audio'
        ? `<div class="waveform">${Array.from({length: 18}, (_,i) =>
            `<div class="waveform-bar" style="height:${30+Math.sin(i)*50}%;animation-delay:${i*0.07}s"></div>`
          ).join('')}</div>`
        : '';
    
    dom.innerHTML = `<div class="trim-handle left"></div><strong style="font-size:0.7rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:calc(100% - 20px);display:block;">${name.split('\\').pop().split('/').pop()}</strong><span class="duration-text">${duration.toFixed(1)}s</span>${extraVisual}<div class="trim-handle right"></div>`;

    // Atualizar posição e largura com base no Zoom
    updateClipVisual(clip, dom);
    
    // Inserir no DOM
    trackElement.appendChild(dom);
    clip.element = dom;
    State.clips.push(clip);

    // Lógica de Mover o Clipe e Fazer Trim
    setupClipInteractions(clip);
    
    // Adicionar botão de transição se for vídeo
    addTransitionButton(clip);
    
    return clip;
}

function updateClipVisual(clip, dom) {
    dom.style.left = (clip.start * State.zoomLevel) + 'px';
    dom.style.width = (clip.duration * State.zoomLevel) + 'px';
    dom.querySelector('.duration-text').innerText = clip.duration.toFixed(1) + 's';
}

function renderTimeline() {
    State.clips.forEach(clip => updateClipVisual(clip, clip.element));
}

// --- 5. LÓGICA DE INTERAÇÃO (Mover e Recortar) ---
function setupClipInteractions(clip) {
    let mode = null; // 'move', 'trim-left', 'trim-right'
    let startX = 0;
    let initialStart = 0;
    let initialDuration = 0;
    let initialTrimIn = 0;

    const onMouseMove = (e) => {
        if (!mode) return;
        
        const deltaX = e.clientX - startX;
        let deltaSeconds = deltaX / State.zoomLevel;
        
        let newStart = initialStart;
        let newDuration = initialDuration;
        let newTrimIn = initialTrimIn;
        
        if (mode === 'move') {
            newStart = initialStart + deltaSeconds;
            if (newStart < 0) newStart = 0;
        } 
        else if (mode === 'trim-right') {
            newDuration = initialDuration + deltaSeconds;
            if (newDuration < 0.5) newDuration = 0.5; // Mínimo 0.5s
        }
        else if (mode === 'trim-left') {
            newStart = initialStart + deltaSeconds;
            newDuration = initialDuration - deltaSeconds;
            newTrimIn = initialTrimIn + deltaSeconds;
            
            if (newStart < 0) {
                newStart = 0;
                newDuration = initialDuration + initialStart;
                newTrimIn = initialTrimIn - initialStart;
            }
            if (newDuration < 0.5) {
                newDuration = 0.5;
                newStart = initialStart + (initialDuration - 0.5);
                newTrimIn = initialTrimIn + (initialDuration - 0.5);
            }
        }
        
        // --- SNAPPING LOGIC ---
        if (typeof isSnappingEnabled !== 'undefined' && isSnappingEnabled) {
            const snapToleranceSeconds = 15 / State.zoomLevel; // 15 pixels de tolerância visual
            const snapPoints = [State.currentTime, 0]; // Agulha e Início absoluto
            State.clips.forEach(c => {
                if (c.id !== clip.id) {
                    snapPoints.push(c.start);
                    snapPoints.push(c.start + c.duration);
                }
            });
            
            let bestSnapDiff = snapToleranceSeconds;
            let snapOffset = 0;
            
            if (mode === 'move') {
                const checkEdges = [newStart, newStart + newDuration];
                snapPoints.forEach(p => {
                    checkEdges.forEach(edge => {
                        const diff = p - edge;
                        if (Math.abs(diff) < Math.abs(bestSnapDiff)) {
                            bestSnapDiff = diff;
                            snapOffset = diff;
                        }
                    });
                });
                if (snapOffset !== 0) {
                    newStart += snapOffset;
                    if (newStart < 0) newStart = 0;
                }
            } else if (mode === 'trim-right') {
                const rightEdge = newStart + newDuration;
                snapPoints.forEach(p => {
                    const diff = p - rightEdge;
                    if (Math.abs(diff) < Math.abs(bestSnapDiff)) {
                        bestSnapDiff = diff;
                        snapOffset = diff;
                    }
                });
                if (snapOffset !== 0) {
                    newDuration += snapOffset;
                    if (newDuration < 0.5) newDuration = 0.5;
                }
            } else if (mode === 'trim-left') {
                snapPoints.forEach(p => {
                    const diff = p - newStart;
                    if (Math.abs(diff) < Math.abs(bestSnapDiff)) {
                        bestSnapDiff = diff;
                        snapOffset = diff;
                    }
                });
                if (snapOffset !== 0) {
                    newStart += snapOffset;
                    newDuration -= snapOffset;
                    newTrimIn += snapOffset;
                    if (newStart < 0) {
                        newStart = 0;
                    }
                    if (newDuration < 0.5) {
                        newDuration = 0.5;
                    }
                }
            }
        }
        
        clip.start = newStart;
        clip.duration = newDuration;
        if (mode === 'trim-left') clip.trimIn = newTrimIn;
        
        updateClipVisual(clip, clip.element);
        updateInspector();
    };

    const onMouseUp = () => {
        if (mode) {
            mode = null;
            clip.element.style.zIndex = '';
            if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
        }
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
    };

    clip.element.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('trim-handle')) {
            mode = e.target.classList.contains('left') ? 'trim-left' : 'trim-right';
        } else {
            mode = 'move';
        }
        
        startX = e.clientX;
        initialStart = clip.start;
        initialDuration = clip.duration;
        initialTrimIn = clip.trimIn;
        clip.element.style.zIndex = '100';

        // Lógica de Seleção
        State.clips.forEach(c => c.element.classList.remove('selected'));
        clip.element.classList.add('selected');
        State.selectedClip = clip;
        updateInspector();

        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
    });
}

// --- 6. AGULHA (PLAYHEAD) E ZOOM ---
UI.zoomSlider.addEventListener('input', (e) => {
    State.zoomLevel = parseInt(e.target.value);
    renderTimeline();
    updatePlayhead();
});

// Scroll do mouse no trilho faz zoom ancorado (Passo 15)
document.querySelector('.timeline-tracks').addEventListener('wheel', (e) => {
    if (e.ctrlKey) {
        e.preventDefault();
        const container = document.getElementById('timeline-tracks');
        const slider = document.getElementById('zoom-slider');
        
        // Determinar o fator de zoom antes e depois
        const oldZoom = State.zoomLevel;
        const delta = e.deltaY < 0 ? 3 : -3;
        const newZoom = Math.min(50, Math.max(1, parseInt(slider.value) + delta));
        
        if (oldZoom === newZoom) return; // Nenhuma mudança necessária
        
        // Descobrir em qual "tempo" da timeline o mouse está apontando
        const rect = container.getBoundingClientRect();
        const mouseX = e.clientX - rect.left; // Posição do mouse na tela
        const scrollX = container.scrollLeft;
        const timeAtMouse = Math.max(0, (mouseX + scrollX - 80) / oldZoom);
        
        // Atualizar o slider (que vai disparar renderTimeline e mudar State.zoomLevel)
        slider.value = newZoom;
        slider.dispatchEvent(new Event('input'));
        
        // Recalcular qual deve ser o scroll para que o 'timeAtMouse' continue embaixo do mouseX
        const newScrollX = (timeAtMouse * newZoom) + 80 - mouseX;
        container.scrollLeft = newScrollX;
    }
}, { passive: false });

function updatePlayhead() {
    UI.playhead.style.left = ((State.currentTime * State.zoomLevel) + 80) + 'px';
    syncPreviewPlayer(); // Passo 9: sincroniza o player de preview
}

// Lógica para arrastar a cabeça da agulha (Playhead Scrubbing)
const playheadHead = document.querySelector('.playhead-head');
let isDraggingPlayhead = false;
if (playheadHead) {
    playheadHead.addEventListener('mousedown', (e) => {
        e.preventDefault(); // Previne seleção de texto
        isDraggingPlayhead = true;
        document.body.style.cursor = 'ew-resize';
    });
    window.addEventListener('mousemove', (e) => {
        if (!isDraggingPlayhead) return;
        const trackContainer = document.getElementById('timeline-tracks');
        const rect = trackContainer.getBoundingClientRect();
        const clickX = e.clientX - rect.left + trackContainer.scrollLeft - 80;
        State.currentTime = Math.max(0, clickX / State.zoomLevel);
        updatePlayhead();
        UI.timeDisplay.innerText = formatTime(State.currentTime);
    });
    window.addEventListener('mouseup', () => {
        if (isDraggingPlayhead) {
            isDraggingPlayhead = false;
            document.body.style.cursor = '';
        }
    });
}

// --- PASSO 9: PLAYER DE PREVIEW SINCRONIZADO ---
const mainPlayer = document.getElementById('main-player');
let previewCurrentClipId = null;

function syncPreviewPlayer() {
    if (!mainPlayer) return;
    
    // Encontra o clipe de vídeo sob a agulha — prioriza a trilha com maior z-order (B-Roll fica acima do V1)
    const videoClip = State.clips
        .filter(c => c.type === 'video')
        .filter(c => {
            // Verifica se a trilha não está mutada ou oculta
            const trackEl = c.element?.parentElement?.closest('.track');
            if (!trackEl) return true;
            const tid = trackEl.dataset.trackId;
            const tState = State.tracks[tid];
            return !tState?.muted && !tState?.hidden;
        })
        .filter(c => State.currentTime >= c.start && State.currentTime < c.start + c.duration)
        .sort((a, b) => {
            // Ordenar por z-order da trilha (maior = prioridade no preview)
            const getZ = (clip) => {
                const trackEl = clip.element?.parentElement?.closest('.track');
                return trackEl ? parseInt(trackEl.dataset.zOrder || '1') : 1;
            };
            return getZ(b) - getZ(a);
        })[0]; // Pega o de maior z-order
    
    if (!videoClip) {
        if (!mainPlayer.paused) mainPlayer.pause();
        return;
    }
    
    // Evita congelamentos: só troca o src se o arquivo de mídia for diferente!
    const newSrc = videoClip.name.startsWith('http') 
        ? videoClip.name 
        : `/api/stream?path=${encodeURIComponent(videoClip.name)}`;
        
    if (mainPlayer.getAttribute('data-current-src') !== newSrc) {
        mainPlayer.setAttribute('data-current-src', newSrc);
        mainPlayer.src = newSrc;
        mainPlayer.load();
    }
    previewCurrentClipId = videoClip.id;
    
    // Sincroniza o tempo interno do vídeo com a posição relativa dentro do clipe
    const clipLocalTime = (State.currentTime - videoClip.start) + (videoClip.trimIn || 0);
    
    // Só corrige sync de tempo para evitar congelamentos (stuttering)
    if (mainPlayer.readyState >= 1 && !mainPlayer.seeking) {
        const threshold = isPlaying ? 0.5 : 0.1; // Maior tolerância durante a reprodução
        if (Math.abs(mainPlayer.currentTime - clipLocalTime) > threshold) {
            mainPlayer.currentTime = clipLocalTime;
        }
    }
    
    // Se está reproduzindo na timeline, toca o player também
    if (isPlaying && mainPlayer.paused && mainPlayer.src) {
        mainPlayer.play().catch(() => {}); // Erro silencioso (autoplay policy)
    } else if (!isPlaying && !mainPlayer.paused) {
        mainPlayer.pause();
    }
}

// Formatar segundos para HH:MM:SS:FF
function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}:${ms.toString().padStart(2,'0')}`;
}

// --- PASSO 10: MÚLTIPLAS TRILHAS DINÂMICAS ---
// Registro de estado de todas as trilhas
State.tracks = {};

function registerTrack(trackEl) {
    const id = trackEl.dataset.trackId;
    const type = trackEl.dataset.trackType || 'video';
    const zOrder = parseInt(trackEl.dataset.zOrder || '1');
    State.tracks[id] = { id, type, zOrder, muted: false, solo: false, hidden: false, volume: 100 };
    
    // Adicionar slider de volume mini ao header
    const header = trackEl.querySelector('.track-header');
    if (header && !header.querySelector('.volume-mini')) {
        const vol = document.createElement('input');
        vol.type = 'range'; vol.min = 0; vol.max = 200; vol.value = 100;
        vol.className = 'volume-mini';
        vol.title = 'Volume da Trilha';
        vol.addEventListener('input', () => { State.tracks[id].volume = parseInt(vol.value); });
        header.appendChild(vol);
    }
    
    // Registrar botões de controle
    const btnMute = trackEl.querySelector('.btn-track-mute');
    const btnSolo = trackEl.querySelector('.btn-track-solo');
    const btnVis = trackEl.querySelector('.btn-track-vis');
    
    if (btnMute) btnMute.addEventListener('click', () => toggleMute(id, trackEl, btnMute));
    if (btnSolo) btnSolo.addEventListener('click', () => toggleSolo(id, trackEl, btnSolo));
    if (btnVis) btnVis.addEventListener('click', () => toggleVisibility(id, trackEl, btnVis));
    
    // Drop zone, click e Razor Hover
    const content = trackEl.querySelector('.track-content');
    if (content) {
        setupDropZone(content);
        setupPlayheadClick(content);
        setupRazorHover(content); // Passo 12
    }
}

function toggleMute(id, trackEl, btn) {
    State.tracks[id].muted = !State.tracks[id].muted;
    trackEl.classList.toggle('muted', State.tracks[id].muted);
    btn.classList.toggle('muted', State.tracks[id].muted);
    btn.textContent = State.tracks[id].muted ? '🔇' : '🔊';
}

function toggleSolo(id, trackEl, btn) {
    State.tracks[id].solo = !State.tracks[id].solo;
    btn.classList.toggle('soloed', State.tracks[id].solo);
    
    // Se há algum solo ativo, mutar todas as outras trilhas
    const hasSolo = Object.values(State.tracks).some(t => t.solo);
    document.querySelectorAll('.track').forEach(el => {
        const tid = el.dataset.trackId;
        if (!tid || !State.tracks[tid]) return;
        const shouldMute = hasSolo && !State.tracks[tid].solo;
        el.classList.toggle('muted', shouldMute);
    });
}

function toggleVisibility(id, trackEl, btn) {
    State.tracks[id].hidden = !State.tracks[id].hidden;
    trackEl.classList.toggle('hidden', State.tracks[id].hidden);
    btn.classList.toggle('hidden-track', State.tracks[id].hidden);
}

let trackCounter = 2; // V1 e A1 já existem

function addTrack(type) {
    trackCounter++;
    const trackId = `track-${type}-${trackCounter}`;
    const defs = {
        'broll':       { icon: '🎥', label: 'B-Roll', clipType: 'video', z: 2 },
        'audio-narr':  { icon: '🎙️', label: 'Narr.',  clipType: 'audio', z: 1 },
        'audio-music': { icon: '🎵', label: 'Música', clipType: 'audio', z: 0 }
    };
    const { icon, label, z } = defs[type] || { icon: '📹', label: 'Extra', z: 1 };
    
    const track = document.createElement('div');
    track.className = 'track video-track';
    track.dataset.trackId = trackId;
    track.dataset.trackType = type;
    track.dataset.zOrder = z;
    track.innerHTML = `
        <div class="track-header">
            <div class="track-label">
                <span class="track-icon">${icon}</span>
                <span class="track-name">${label}</span>
            </div>
            <div class="track-controls">
                <button class="btn-track-mute btn-icon" title="Mute" data-track-id="${trackId}">🔊</button>
                <button class="btn-track-vis btn-icon" title="Ocultar" data-track-id="${trackId}">👁️</button>
                <button class="btn-icon" title="Remover trilha" onclick="
                    const track = this.closest('.track');
                    const content = track.querySelector('.track-content');
                    if (content && content._cleanupRazor) content._cleanupRazor();
                    State.clips.forEach(c => { if(c.element.parentElement === content) c.element.remove(); });
                    State.clips = State.clips.filter(c => c.element.parentElement !== content);
                    track.remove();
                    delete State.tracks['${trackId}'];
                ">🗑️</button>
            </div>
        </div>
        <div class="track-content" id="${trackId}-content"></div>
    `;
    
    const addBtn = document.getElementById('btn-add-track-row');
    document.getElementById('timeline-tracks').insertBefore(track, addBtn);
    registerTrack(track);
    return track.querySelector('.track-content');
}

// Extrair a lógica de drop para ser reutilizável por qualquer trilha
function setupDropZone(track) {
    track.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        track.style.backgroundColor = 'rgba(139, 92, 246, 0.1)';
    });
    track.addEventListener('dragleave', () => {
        track.style.backgroundColor = 'transparent';
    });
    track.addEventListener('drop', (e) => {
        e.preventDefault();
        track.style.backgroundColor = 'transparent';
        let data;
        try {
            data = JSON.parse(e.dataTransfer.getData('text/plain'));
        } catch (ex) {
            console.warn('[Apollo] Drop inválido — dado não é um clipe Apollo:', ex);
            return;
        }
        if (!data || !data.name) return;
        const trackRect = track.getBoundingClientRect();
        const dropX = e.clientX - trackRect.left + track.scrollLeft;
        let startTime = Math.max(0, dropX / State.zoomLevel);
        createClip(data.name, data.type, startTime, data.duration, data.color, track, 0.0, data.width || 0, data.height || 0);
        
        // Inteligência: Ajusta a proporção automaticamente se for o 1º vídeo e estiver em 'auto'
        if (State.projectRatio === 'auto' && State.clips.filter(c => c.type === 'video').length === 1) {
            if (typeof applyProjectRatio === 'function') applyProjectRatio();
        }
        if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
    });
}

function setupPlayheadClick(track) {
    track.addEventListener('click', (e) => {
        if(e.target.classList.contains('timeline-clip') || e.target.classList.contains('trim-handle')) return;
        const rect = track.getBoundingClientRect();
        const clickX = e.clientX - rect.left + track.scrollLeft - 80;
        State.currentTime = Math.max(0, clickX / State.zoomLevel);
        updatePlayhead();
        UI.timeDisplay.innerText = formatTime(State.currentTime);
    });
}

// Registrar as trilhas existentes no HTML
document.querySelectorAll('.track[data-track-id]').forEach(registerTrack);

// Adicionar o botão de nova trilha na interface
const addTrackRow = document.createElement('div');
addTrackRow.id = 'btn-add-track-row';
addTrackRow.style.cssText = 'padding: 6px 0; background: #0f172a; border-top: 1px dashed #1e293b;';
addTrackRow.innerHTML = `
    <div style="display:flex; gap:6px; padding:4px 84px; align-items:center;">
        <span style="font-size:0.7rem;color:#475569;white-space:nowrap;">+ Trilha:</span>
        <button class="btn-add-track" onclick="addTrack('broll')">B-Roll 🎥</button>
        <button class="btn-add-track" onclick="addTrack('audio-narr')">Narração 🎙️</button>
        <button class="btn-add-track" onclick="addTrack('audio-music')">Música 🎵</button>
    </div>
`;
document.getElementById('timeline-tracks').appendChild(addTrackRow);

// Inicialização (após todas as trilhas e drop zones serem configuradas)
renderTimeline();
updatePlayhead();

// ============================================================
// === PASSO 11: PLAYBACK ENGINE — SINCRONIA MULTITRACK      ===
// ============================================================

// --- Estado central do Motor ---
let isPlaying = false;
let playStartWallTime = 0;    // performance.now() no momento em que o Play foi apertado
let playStartProjectTime = 0; // State.currentTime no momento em que o Play foi apertado
let playbackRateVal = 1.0;    // 0.5 | 1.0 | 2.0
let loopEnabled = false;
let rafId = null;

// Pool de <audio> elements para clipes de áudio
const audioPool = new Map(); // clipId → HTMLAudioElement

const btnPlay = document.getElementById('btn-play');

// --- Controles extras na barra de controle ---
const controlsBar = document.querySelector('.player-controls');
controlsBar.insertAdjacentHTML('beforeend', `
    <select id="playback-rate" title="Velocidade de reprodução" style="background:#1e293b;border:1px solid #334155;color:#f8fafc;padding:3px 6px;border-radius:4px;font-size:0.8rem;cursor:pointer;">
        <option value="0.5">0.5×</option>
        <option value="1" selected>1×</option>
        <option value="2">2×</option>
    </select>
    <button id="btn-loop" title="Repetir" style="background:#1e293b;border:1px solid #334155;color:#94a3b8;padding:4px 8px;border-radius:4px;font-size:0.8rem;cursor:pointer;">🔁 Loop</button>
    <button id="btn-rewind" title="Voltar ao início" style="background:#1e293b;border:1px solid #334155;color:#94a3b8;padding:4px 8px;border-radius:4px;font-size:0.8rem;cursor:pointer;">⏮ Início</button>
`);

document.getElementById('playback-rate').addEventListener('change', (e) => {
    playbackRateVal = parseFloat(e.target.value);
    // Resinc: ajustar ponto de partida para evitar salto de tempo
    if (isPlaying) {
        playStartWallTime = performance.now();
        playStartProjectTime = State.currentTime;
    }
    // Aplicar velocidade nos players ativos
    if (mainPlayer) mainPlayer.playbackRate = playbackRateVal;
    audioPool.forEach(a => { a.playbackRate = playbackRateVal; });
});

document.getElementById('btn-loop').addEventListener('click', (e) => {
    loopEnabled = !loopEnabled;
    e.target.style.color = loopEnabled ? '#8b5cf6' : '#94a3b8';
    e.target.style.borderColor = loopEnabled ? '#8b5cf6' : '#334155';
});

document.getElementById('btn-rewind').addEventListener('click', () => {
    const wasPlaying = isPlaying;
    if (isPlaying) togglePlay();
    State.currentTime = 0;
    updatePlayhead();
    UI.timeDisplay.innerText = formatTime(0);
    if (wasPlaying) togglePlay();
});

// --- Duração total do projeto ---
function getProjectDuration() {
    if (State.clips.length === 0) return 0;
    return Math.max(...State.clips.map(c => c.start + c.duration));
}

// --- Gerenciar os <audio> elements de cada clipe de áudio ---
function syncAudioClips() {
    const now = State.currentTime;

    State.clips.forEach(clip => {
        if (clip.type !== 'audio') return;

        // Verificar se a trilha não está mutada
        const trackEl = clip.element?.parentElement?.closest('.track');
        const tid = trackEl?.dataset?.trackId;
        const tState = tid ? State.tracks[tid] : null;
        const trackMuted = tState?.muted || tState?.hidden || false;
        const trackVolume = tState ? tState.volume / 100 : 1.0;

        const clipActive = now >= clip.start && now < clip.start + clip.duration;

        if (!audioPool.has(clip.id)) {
            audioPool.set(clip.id, new Audio());
        }
        const audioEl = audioPool.get(clip.id);

        if (clipActive && !trackMuted) {
            // Definir src se ainda não definido para este clipe
            if (!audioEl.dataset.clipId || audioEl.dataset.clipId !== String(clip.id)) {
                audioEl.src = `/api/stream?path=${encodeURIComponent(clip.name)}`;
                audioEl.dataset.clipId = clip.id;
                audioEl.load();
            }

            // Sincronizar tempo interno
            const localTime = (now - clip.start) + (clip.trimIn || 0);
            if (Math.abs(audioEl.currentTime - localTime) > 0.4) {
                audioEl.currentTime = localTime;
            }
            audioEl.volume = Math.min(1.0, trackVolume);
            audioEl.playbackRate = playbackRateVal;

            if (isPlaying && audioEl.paused) {
                audioEl.play().catch(() => {});
            }
        } else {
            // Clipe fora do range — pausar e "devolver ao pool"
            if (!audioEl.paused) {
                audioEl.pause();
            }
        }
    });
}

// --- Destacar visualmente o clipe em reprodução ---
function highlightActiveClips() {
    State.clips.forEach(clip => {
        const active = State.currentTime >= clip.start && State.currentTime < clip.start + clip.duration;
        if (clip.element) {
            clip.element.classList.toggle('playing', active);
        }
    });
}

// --- O LOOP PRINCIPAL (requestAnimationFrame) ---
function playbackLoop(now) {
    if (!isPlaying) return;

    // Relógio-mestre: calcula o tempo de projeto usando wall-clock (evita drift acumulado)
    const elapsed = (now - playStartWallTime) / 1000 * playbackRateVal;
    State.currentTime = playStartProjectTime + elapsed;

    const projectDuration = getProjectDuration();

    // Auto-parada no fim do projeto
    if (projectDuration > 0 && State.currentTime >= projectDuration) {
        if (loopEnabled) {
            // Reinicia
            playStartWallTime = now;
            playStartProjectTime = 0;
            State.currentTime = 0;
        } else {
            State.currentTime = projectDuration;
            updatePlayhead();
            UI.timeDisplay.innerText = formatTime(State.currentTime);
            highlightActiveClips();
            togglePlay(); // Para automaticamente
            return;
        }
    }

    updatePlayhead();
    UI.timeDisplay.innerText = formatTime(State.currentTime);
    syncAudioClips();
    highlightActiveClips();

    rafId = requestAnimationFrame(playbackLoop);
}

// --- Toggle Play / Pause ---
function togglePlay() {
    isPlaying = !isPlaying;
    btnPlay.innerText = isPlaying ? '⏸ Pause' : '▶ Play';

    if (isPlaying) {
        // Captura o ponto de partida no relógio de parede
        playStartWallTime = performance.now();
        playStartProjectTime = State.currentTime;
        rafId = requestAnimationFrame(playbackLoop);
    } else {
        // Pause: cancelar RAF e pausar todos os áudios
        if (rafId) cancelAnimationFrame(rafId);
        if (mainPlayer && !mainPlayer.paused) mainPlayer.pause();
        audioPool.forEach(a => { if (!a.paused) a.pause(); });
        highlightActiveClips(); // Limpa o destaque
    }
}

btnPlay.addEventListener('click', togglePlay);


// --- 8. INSPETOR E FERRAMENTAS (Fase 3 & Passo 14) ---
function updateInspector() {
    const content = document.getElementById('inspector-content');
    if (!State.selectedClip) {
        content.innerHTML = '<p class="empty-text">Selecione um clipe na timeline.</p>';
        return;
    }
    const c = State.selectedClip;
    
    // Garantir que as propriedades default existam
    c.volume = c.volume !== undefined ? c.volume : 100;
    c.opacity = c.opacity !== undefined ? c.opacity : 100;
    c.scale = c.scale !== undefined ? c.scale : 100;
    c.posX = c.posX !== undefined ? c.posX : 0;
    c.posY = c.posY !== undefined ? c.posY : 0;

    content.innerHTML = `
        <div class="inspector-form">
            <div style="background:#1e293b; padding:8px; border-radius:6px; margin-bottom:10px;">
                <h4 style="color:white; margin:0; font-size:0.85rem; word-break:break-all;">
                    ${c.type==='video'?'🎬':'🎵'} ${c.name.split('\\').pop().split('/').pop()}
                </h4>
            </div>

            <div style="display:flex; gap:10px;">
                <div style="flex:1;">
                    <label>Início (s)</label>
                    <input type="number" step="0.1" value="${c.start.toFixed(2)}" readonly style="background:#0f172a; color:#64748b;">
                </div>
                <div style="flex:1;">
                    <label>Duração (s)</label>
                    <input type="number" step="0.1" value="${c.duration.toFixed(2)}" readonly style="background:#0f172a; color:#64748b;">
                </div>
            </div>

            <div style="margin-top:10px; border-top:1px solid #334155; padding-top:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <label>Volume (%)</label>
                    <span id="insp-vol-val" style="font-size:0.75rem;color:#8b5cf6;">${c.volume}%</span>
                </div>
                <input type="range" id="insp-vol" min="0" max="200" value="${c.volume}">
            </div>

            ${c.type === 'video' ? `
            <div style="margin-top:10px; border-top:1px solid #334155; padding-top:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <label>Opacidade (%)</label>
                    <span id="insp-op-val" style="font-size:0.75rem;color:#8b5cf6;">${c.opacity}%</span>
                </div>
                <input type="range" id="insp-op" min="0" max="100" value="${c.opacity}">
                
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px;">
                    <label>Escala (%)</label>
                    <span id="insp-scale-val" style="font-size:0.75rem;color:#8b5cf6;">${c.scale}%</span>
                </div>
                <input type="range" id="insp-scale" min="10" max="300" value="${c.scale}">

                <div style="display:flex; gap:10px; margin-top:10px;">
                    <div style="flex:1;">
                        <label>Pos X (px)</label>
                        <input type="number" id="insp-posx" value="${c.posX}">
                    </div>
                    <div style="flex:1;">
                        <label>Pos Y (px)</label>
                        <input type="number" id="insp-posy" value="${c.posY}">
                    </div>
                </div>
                <div style="font-size:0.65rem; color:#64748b; margin-top:4px;">
                    Dica: Use 0,0 para centro da tela.
                </div>
            </div>
            ` : ''}

            ${c.type === 'text' ? `
            <div style="margin-top:10px; border-top:1px solid #334155; padding-top:10px;">
                <label>Texto:</label>
                <input type="text" id="insp-text" value="${c.textContent}" style="width:100%; margin-bottom:10px; background:#0f172a; color:white; border:1px solid #334155; padding:5px; border-radius:4px;">
                
                <div style="display:flex; gap:10px; margin-bottom:10px;">
                    <div style="flex:1;">
                        <label>Tamanho Fonte</label>
                        <input type="number" id="insp-fontsize" value="${c.fontSize}" style="width:100%; background:#0f172a; color:white; border:1px solid #334155; padding:5px; border-radius:4px;">
                    </div>
                    <div style="flex:1;">
                        <label>Cor Fonte</label>
                        <input type="color" id="insp-fontcolor" value="${c.fontColor}" style="width:100%; height:30px; border:none; background:transparent;">
                    </div>
                </div>

                <div style="display:flex; gap:10px; margin-bottom:10px;">
                    <div style="flex:1;">
                        <label>Pos X (px)</label>
                        <input type="number" id="insp-text-posx" value="${c.posX}" style="width:100%; background:#0f172a; color:white; border:1px solid #334155; padding:5px; border-radius:4px;">
                    </div>
                    <div style="flex:1;">
                        <label>Pos Y (px)</label>
                        <input type="number" id="insp-text-posy" value="${c.posY}" style="width:100%; background:#0f172a; color:white; border:1px solid #334155; padding:5px; border-radius:4px;">
                    </div>
                </div>

                <div style="margin-top:15px; background:#0f172a; padding:10px; border-radius:6px; border:1px solid #334155;">
                    <h5 style="margin-top:0; color:#8b5cf6; font-size:0.8rem; margin-bottom:8px;">💾 Presets de Texto</h5>
                    <div style="display:flex; gap:5px; margin-bottom:5px;">
                        <input type="text" id="preset-name" placeholder="Nome do preset" style="flex:1; font-size:0.75rem; background:#1e293b; color:white; border:1px solid #334155; padding:4px; border-radius:3px;">
                        <button class="btn secondary mini" id="btn-save-preset" style="padding:4px 8px; font-size:0.75rem;">Salvar</button>
                    </div>
                    <div style="display:flex; gap:5px;">
                        <select id="preset-list" style="flex:1; font-size:0.75rem; background:#1e293b; color:white; border:1px solid #334155; padding:4px; border-radius:3px;"></select>
                        <button class="btn secondary mini" id="btn-load-preset" style="padding:4px 8px; font-size:0.75rem;">Aplicar</button>
                    </div>
                </div>
            </div>
            ` : ''}
        </div>
    `;

    // Conectar eventos (binding)
    const setVal = (id, field) => {
        const el = document.getElementById(id);
        const disp = document.getElementById(id + '-val');
        if (!el) return;
        el.addEventListener('input', (e) => {
            let val = e.target.value;
            if (e.target.type !== 'text' && e.target.type !== 'color') val = parseFloat(val);
            
            c[field] = val;
            if (disp) disp.innerText = val + (field==='posX'||field==='posY'?'px': (typeof val === 'number' ? '%' : ''));
            
            if (field === 'textContent' && c.element) {
                const strong = c.element.querySelector('strong');
                if (strong) strong.innerText = c.textContent;
            }
            
            applyLivePreview(c);
        });
    };

    setVal('insp-vol', 'volume');
    if (c.type === 'video') {
        setVal('insp-op', 'opacity');
        setVal('insp-scale', 'scale');
        
        document.getElementById('insp-posx').addEventListener('input', (e) => { c.posX = parseInt(e.target.value)||0; applyLivePreview(c); });
        document.getElementById('insp-posy').addEventListener('input', (e) => { c.posY = parseInt(e.target.value)||0; applyLivePreview(c); });
    }

    if (c.type === 'text') {
        setVal('insp-text', 'textContent');
        setVal('insp-fontsize', 'fontSize');
        setVal('insp-fontcolor', 'fontColor');
        document.getElementById('insp-text-posx').addEventListener('input', (e) => { c.posX = parseInt(e.target.value)||0; });
        document.getElementById('insp-text-posy').addEventListener('input', (e) => { c.posY = parseInt(e.target.value)||0; });
        
        if (typeof window.loadTextPresetList === 'function') window.loadTextPresetList();

        const btnSave = document.getElementById('btn-save-preset');
        if (btnSave) btnSave.addEventListener('click', async () => {
            const name = document.getElementById('preset-name').value;
            if (!name) return alert('Digite o nome do preset');
            const data = { font_size: c.fontSize, font_color: c.fontColor, pos_x: c.posX, pos_y: c.posY };
            await fetch('https://api.apolloedit.com/api/save_profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nome: 'text_preset_' + name, template_data: data })
            });
            alert('Preset salvo!');
            window.loadTextPresetList();
        });

        const btnLoad = document.getElementById('btn-load-preset');
        if (btnLoad) btnLoad.addEventListener('click', async () => {
            const name = document.getElementById('preset-list').value;
            if (!name) return;
            const res = await fetch('https://api.apolloedit.com/api/load_profile?nome=' + encodeURIComponent(name));
            const data = await res.json();
            if (data.status === 'success' && data.template_data) {
                c.fontSize = data.template_data.font_size || c.fontSize;
                c.fontColor = data.template_data.font_color || c.fontColor;
                c.posX = data.template_data.pos_x || c.posX;
                c.posY = data.template_data.pos_y || c.posY;
                updateInspector();
            }
        });
    }
}

window.loadTextPresetList = async function() {
    const select = document.getElementById('preset-list');
    if (!select) return;
    try {
        const res = await fetch('https://api.apolloedit.com/api/list_profiles');
        const data = await res.json();
        if (data.status === 'success') {
            select.innerHTML = '<option value="">Selecione...</option>';
            data.perfis.filter(p => p.startsWith('text_preset_')).forEach(p => {
                select.innerHTML += `<option value="${p}">${p.replace('text_preset_', '')}</option>`;
            });
        }
    } catch(e) {}
}

// Aplica propriedades em tempo real no preview HTML (apenas aproximação visual para o browser)
function applyLivePreview(clip) {
    if (clip.type === 'video' && mainPlayer && previewCurrentClipId === clip.id) {
        mainPlayer.volume = Math.min(1.0, clip.volume / 100);
        mainPlayer.style.opacity = clip.opacity / 100;
        mainPlayer.style.transform = `translate(${clip.posX}px, ${clip.posY}px) scale(${clip.scale / 100})`;
    }
    if (clip.type === 'audio' && audioPool.has(clip.id)) {
        const a = audioPool.get(clip.id);
        a.volume = Math.min(1.0, clip.volume / 100);
    }
}


// Atalhos de Teclado
window.addEventListener('keydown', (e) => {
    // Espaço para Play/Pause (sem interrupcao de foco)
    if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA' && !e.target.isContentEditable) {
        e.preventDefault();
        togglePlay();
    }
    
    // Zoom In (Ctrl + ou Ctrl =)
    if (e.ctrlKey && (e.key === '+' || e.key === '=')) {
        e.preventDefault();
        const slider = document.getElementById('zoom-slider');
        if(slider) {
            slider.value = Math.min(parseInt(slider.max || 50), parseInt(slider.value) + 5);
            slider.dispatchEvent(new Event('input'));
        }
    }
    
    // Zoom Out (Ctrl -)
    if (e.ctrlKey && e.key === '-') {
        e.preventDefault();
        const slider = document.getElementById('zoom-slider');
        if(slider) {
            slider.value = Math.max(parseInt(slider.min || 1), parseInt(slider.value) - 5);
            slider.dispatchEvent(new Event('input'));
        }
    }
    
    // Deletar clipe
    if ((e.code === 'Delete' || e.code === 'Backspace') && State.selectedClip && e.target.tagName !== 'INPUT') {
        const idx = State.clips.indexOf(State.selectedClip);
        if (idx > -1) {
            State.selectedClip.element.remove();
            State.clips.splice(idx, 1);
            State.selectedClip = null;
            updateInspector();
            if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
        }
    }
    
    // Ativa Select Tool (V)
    if (e.code === 'KeyV' && e.target.tagName !== 'INPUT') {
        setActiveTool('select');
    }

    // Ativa Razor Tool (B)
    if (e.code === 'KeyB' && e.target.tagName !== 'INPUT') {
        setActiveTool('razor');
    }

    // Toggle Magnet/Snapping (S)
    if (e.code === 'KeyS' && e.target.tagName !== 'INPUT') {
        toggleSnapping();
    }

    // Ferramenta Gilete (Cortar ao meio com a tecla C)
    if (e.code === 'KeyC' && State.selectedClip && e.target.tagName !== 'INPUT') {
        const c = State.selectedClip;
        // Verifica se a playhead está em cima do clipe selecionado
        if (State.currentTime > c.start && State.currentTime < c.start + c.duration) {
            const cutPoint = State.currentTime;
            const originalDuration = c.duration;
            
            // Ajusta o clipe original para terminar no corte
            c.duration = cutPoint - c.start;
            updateClipVisual(c, c.element);
            
            // Cria um novo clipe a partir do corte
            const trackEl = c.element.parentElement;
            createClip(c.name + ' (Corte)', c.type, cutPoint, originalDuration - c.duration, c.color, trackEl);
        }
    }
});

// --- 9. EXPORTAÇÃO E SALVAMENTO (Fase 4 & Passo 16) ---

function serializeProject() {
    return {
        project_name: "apollo_timeline_v1",
        export_time: new Date().toISOString(),
        clips: State.clips.map(c => ({
            id: c.id,
            name: c.name,
            type: c.type,
            start_time: c.start,
            duration: c.duration,
            trim_in: c.trimIn,
            track: c.element.parentElement.id,
            color: c.color,
            // Passo 14: Propriedades do Inspetor
            volume: c.volume !== undefined ? c.volume : 100,
            opacity: c.opacity !== undefined ? c.opacity : 100,
            scale: c.scale !== undefined ? c.scale : 100,
            pos_x: c.posX !== undefined ? c.posX : 0,
            pos_y: c.posY !== undefined ? c.posY : 0,
            text_content: c.textContent !== undefined ? c.textContent : "",
            font_size: c.fontSize !== undefined ? c.fontSize : 48,
            font_color: c.fontColor !== undefined ? c.fontColor : "#ffffff"
        })).sort((a, b) => a.start_time - b.start_time),
        // Passo 13: incluir transições no JSON
        transitions: State.transitions.map(t => ({
            id: t.id,
            type: t.type,
            duration: t.duration,
            left_clip_id: t.leftClipId,
            right_clip_id: t.rightClipId
        }))
    };
}

function loadProject(jsonString) {
    try {
        const data = JSON.parse(jsonString);
        
        // 1. Limpar timeline atual
        if (isPlaying) togglePlay(); // Pausa a reprodução
        
        State.clips.forEach(c => c.element.remove());
        State.clips = [];
        
        State.transitions.forEach(t => { if (t.element) t.element.remove(); });
        State.transitions = [];
        
        State.selectedClip = null;
        updateInspector();
        
        // 2. Reconstruir clipes
        let maxId = 1;
        data.clips.forEach(c => {
            const trackEl = document.getElementById(c.track);
            if (!trackEl) {
                console.warn(`Trilha ${c.track} não encontrada para o clipe ${c.name}`);
                return;
            }
            
            const color = c.color || (c.type === 'video' ? '#3b82f6' : '#f97316');
            createClip(c.name, c.type, c.start_time, c.duration, color, trackEl, c.trim_in);
            
            const newClip = State.clips[State.clips.length - 1];
            newClip.id = c.id; // Mantém IDs consistentes para transições
            newClip.volume = c.volume !== undefined ? c.volume : 100;
            newClip.opacity = c.opacity !== undefined ? c.opacity : 100;
            newClip.scale = c.scale !== undefined ? c.scale : 100;
            newClip.posX = c.pos_x || 0;
            newClip.posY = c.pos_y || 0;
            
            if (c.id > maxId) maxId = c.id;
        });
        
        // 3. Reconstruir transições
        if (data.transitions) {
            data.transitions.forEach(t => {
                const leftClip = State.clips.find(c => c.id === t.left_clip_id);
                const rightClip = State.clips.find(c => c.id === t.right_clip_id);
                if (leftClip && rightClip) {
                    const newTrans = createTransitionBlock(leftClip, rightClip, t.type, t.duration);
                    if (newTrans) newTrans.id = t.id;
                    if (t.id > maxId) maxId = t.id;
                }
            });
        }
        
        State.nextId = maxId + 1;
        State.currentTime = 0;
        updatePlayhead();
        renderTimeline();
        
        alert('Projeto carregado com sucesso!');
    } catch(err) {
        alert('Erro ao carregar projeto: Arquivo inválido ou corrompido.');
        console.error(err);
    }
}

// Função genérica para enviar job pro back-end
function sendToPython(draftMode = false, config = null) {
    const exportData = serializeProject();
    exportData.draft_mode = draftMode;
    if (config) {
        exportData.export_resolution = config.resolution;
        exportData.export_fps = config.fps;
        exportData.export_quality = config.quality;
    }

    fetch('https://api.apolloedit.com/api/export_timeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            startRenderPolling(); // Inicia o monitoramento de progresso!
        } else {
            alert("Erro na exportação: " + data.message);
        }
    })
    .catch(err => {
        alert("Erro de conexão com o servidor Python. Ele está rodando?");
        console.error(err);
    });
}

// Botão "Exportar para Python" (Renderizar HD)
// Eventos da Modal de Exportacao
document.getElementById('btn-export').addEventListener('click', () => {
    document.getElementById('export-modal').style.display = 'flex';
});

// VARIAVEL GLOBAL PARA SALVAR AS OPÇÕES ESCOLHIDAS ANTES DO CHECKOUT
window.currentExportOptions = null;

document.getElementById('btn-confirm-export')?.addEventListener('click', () => {
    const res = document.getElementById('export-resolution').value;
    const fps = document.getElementById('export-fps').value;
    const qual = document.getElementById('export-quality').value;
    
    document.getElementById('export-modal').style.display = 'none';
    
    // Salva para usar depois que pagar
    window.currentExportOptions = { resolution: res, fps: fps, quality: qual };
    
    // Calcula complexidade (exemplo simplificado: duração do projeto em segundos)
    const durationSec = UI.duration * 10; // (exemplo de fallback)
    
    // Abre a tela de Checkout simulando chamada de API de Orçamento
    document.getElementById('checkout-nitro-modal').style.display = 'flex';
    document.getElementById('checkout-offers-container').innerHTML = '<p style="text-align:center; color:#94a3b8;">Calculando Estimativa de Tempo (ETA)...</p>';
    
    // Chama nosso novo Checkout Engine no Backend
    fetch('https://api.apolloedit.com/api/calculate_budget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            job_type: "video_render",
            duration_seconds: Math.max(30, durationSec), // minimo 30s
            complexity_score: 1.5 // Multiplicador de transições/filtros
        })
    }).then(r => r.json())
      .then(budget => {
         renderCheckoutOffers(budget.options);
      }).catch(e => {
         console.error(e);
         document.getElementById('checkout-offers-container').innerHTML = '<p style="color:#ef4444;">Erro ao calcular ETA.</p>';
      });
});

function renderCheckoutOffers(options) {
    const container = document.getElementById('checkout-offers-container');
    container.innerHTML = '';
    
    const offerCards = [
        { key: 'free_tier', data: options.free_tier, color: '#64748b', icon: '🐢', invId: null },
        { key: 'nitro_tier', data: options.nitro_tier, color: '#8b5cf6', icon: '🚀', invId: 'nitro_t4' },
        { key: 'nitro_master_tier', data: options.nitro_master_tier, color: '#f59e0b', icon: '⚡', invId: 'nitro_a100' }
    ];
    
    // Pegar o inventário do usuário para ver se ele tem o item
    const inventory = window.ApolloEconomy ? window.ApolloEconomy.getInventory() : {};
    
    offerCards.forEach(offer => {
        const d = offer.data;
        const btn = document.createElement('div');
        btn.style.cssText = `
            border: 2px solid #334155; border-radius: 8px; padding: 15px; 
            display:flex; justify-content:space-between; align-items:center; cursor:pointer; 
            transition: all 0.2s; background: rgba(0,0,0,0.3);
        `;
        btn.onmouseover = () => btn.style.borderColor = offer.color;
        btn.onmouseout = () => btn.style.borderColor = '#334155';
        
        // Se tem o item no bagageiro, a oferta muda
        const hasItemInBag = offer.invId && inventory[offer.invId] && inventory[offer.invId] > 0;
        
        let priceTagHTML = '';
        if (hasItemInBag) {
             priceTagHTML = `
                <span style="display:block; font-size:1rem; font-weight:bold; color:#10b981;">
                    USAR DO BAGAGEIRO (x${inventory[offer.invId]})
                </span>
                <span style="color:#64748b; font-size:0.75rem;">Não gasta Cristais/Moedas</span>
             `;
        } else {
             priceTagHTML = `
                <span style="display:block; font-size:1.2rem; font-weight:bold; color:#f8fafc;">
                    ${d.cost_value} ${d.cost_currency === 'apollo_coins' ? '🪙' : '💎'}
                </span>
                <span style="color:#64748b; font-size:0.75rem;">Pagar na hora</span>
             `;
        }
        
        btn.innerHTML = `
            <div>
                <h3 style="margin:0; color:${offer.color}; font-size:1.1rem;">${offer.icon} ${d.title}</h3>
                <p style="margin:4px 0 0 0; color:#94a3b8; font-size:0.85rem;">${d.marketing_tag}</p>
                <div style="margin-top:8px; font-family:monospace; color:#cbd5e1; background:#0f172a; padding:4px 8px; border-radius:4px; display:inline-block;">
                    ETA: ${d.eta_formatted}
                </div>
            </div>
            <div style="text-align:right;">
                ${priceTagHTML}
            </div>
        `;
        
        btn.onclick = () => {
            if (window.ApolloEconomy) {
                 if (hasItemInBag) {
                     window.ApolloEconomy.useItem(offer.invId);
                 } else {
                     const success = d.cost_currency === 'crystals' 
                        ? window.ApolloEconomy.deductCrystals(d.cost_value)
                        : window.ApolloEconomy.deductCoins(d.cost_value);
                     
                     if (!success) {
                         alert('Você não tem saldo suficiente. Compre mais recursos na Loja ou ganhe Moedas vendo Ad!');
                         return; // Cancela se não tem saldo
                     }
                 }
            }
            
            document.getElementById('checkout-nitro-modal').style.display = 'none';
            window.currentRenderETA = d.eta_seconds; 
            sendToPython(false, window.currentExportOptions);
        };
        
        container.appendChild(btn);
    });
}

// Botão "Auto-Edit IA" (O Diretor IA na Timeline)
document.getElementById('btn-ai-edit')?.addEventListener('click', () => {
    const exportData = serializeProject();
    
    // Inicia a barra de progresso (a IA vai atualizar render_status.json durante o processo)
    startRenderPolling();
    
    // Muda a cor da barra para roxo mágico
    setTimeout(() => {
        const bar = document.getElementById('render-progress-bar');
        if (bar) bar.style.background = 'linear-gradient(90deg, #b534ff, #8b5cf6)';
    }, 100);

    fetch('https://api.apolloedit.com/api/ai_edit_timeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            loadProject(JSON.stringify(data.data));
            // Dá um feedback visual na agulha
            document.getElementById('btn-ai-edit').innerText = '✅ IA Aplicada!';
            setTimeout(() => {
                document.getElementById('btn-ai-edit').innerText = '🪄 Auto-Edit IA';
            }, 3000);
        } else {
            alert("Erro na IA: " + data.message);
        }
    })
    .catch(err => {
        alert("Erro de conexão com o servidor Python. Verifique o console.");
        console.error(err);
    });
});

// Botão "Rascunho Rápido" (Renderizar SD/Ultrafast)
document.getElementById('btn-draft').addEventListener('click', () => sendToPython(true));

// Botão "Salvar Projeto" (Baixar .json local)
document.getElementById('btn-save-project').addEventListener('click', () => {
    const exportData = serializeProject();
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 4));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", "apollo_projeto.json");
    dlAnchorElem.click();
});

// Botão "Abrir Projeto" (Carregar .json local)
const loadInput = document.getElementById('file-load-project');
document.getElementById('btn-load-project').addEventListener('click', () => {
    loadInput.click();
});

loadInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
        loadProject(event.target.result);
        loadInput.value = ''; // Reset para permitir carregar o mesmo arquivo novamente
    };
    reader.readAsText(file);
});

// --- 10. INTEGRAÇÃO REAL DE MÍDIA COM FFPROBE (Parte 7) ---
const btnImport = document.querySelector('.media-library .btn-icon');
if (btnImport) {
    btnImport.addEventListener('click', () => {
        fetch('https://api.apolloedit.com/api/browse_file')
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success' && data.paths && data.paths.length > 0) {
                    data.paths.forEach(path => {
                        const name = path.split('/').pop().split('\\').pop();
                        
                        // Usa FFprobe para ler a duração REAL do arquivo
                        fetch(`/api/probe_file?path=${encodeURIComponent(path)}`)
                            .then(r => r.json())
                            .then(probe => {
                                const realDuration = probe.status === 'success' ? probe.duration : 10.0;
                                
                                // Fallback de segurança caso o FFprobe falhe no Windows
                                let isVideo = false;
                                if (probe.status === 'success') {
                                    isVideo = probe.has_video;
                                } else {
                                    const ext = path.split('.').pop().toLowerCase();
                                    isVideo = ['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(ext);
                                }
                                const grid = document.getElementById('media-grid');
                                const div = document.createElement('div');
                                div.className = 'media-item';
                                div.draggable = true;
                                div.dataset.type = isVideo ? 'video' : 'audio';
                                div.dataset.duration = realDuration;
                                div.dataset.path = path;
                                
                                const durStr = realDuration >= 60
                                    ? `${Math.floor(realDuration/60)}m${(realDuration%60).toFixed(0)}s`
                                    : `${realDuration.toFixed(1)}s`;
                                
                                div.innerHTML = `
                                    <div class="media-thumb ${isVideo ? 'bg-blue' : 'bg-orange'}">${isVideo ? '🎥' : '🎵'}</div>
                                    <div class="media-info" style="font-size:0.7rem; word-break:break-all;">${name}<br><span>${durStr}</span></div>
                                `;
                                
                                div.addEventListener('dragstart', (e) => {
                                    e.dataTransfer.setData('text/plain', JSON.stringify({
                                        type: div.dataset.type,
                                        duration: realDuration,
                                        name: path,
                                        color: isVideo ? '#3b82f6' : '#f97316',
                                        width: probe.width || 0,
                                        height: probe.height || 0
                                    }));
                                    e.dataTransfer.effectAllowed = 'copy';
                                });
                                
                                grid.appendChild(div);
                            });
                    });
                }
            });
    });
}

// --- 11. BARRA DE PROGRESSO DE RENDERIZAÇÃO (Parte 7) ---
let renderPollInterval = null;

function startRenderPolling() {
    // Criar barra de progresso dinamicamente
    let bar = document.getElementById('render-progress-bar');
    if (!bar) {
        const container = document.createElement('div');
        container.id = 'render-progress-container';
        container.style.cssText = `
            position: fixed; bottom: 0; left: 0; right: 0; 
            background: #0f172a; border-top: 2px solid #8b5cf6;
            padding: 10px 20px; z-index: 9999;
            display: flex; align-items: center; gap: 15px;
        `;
        container.innerHTML = `
            <span style="color:#8b5cf6; font-weight:bold;">🎬 Renderizando:</span>
            <div style="flex:1; background:#1e293b; height:12px; border-radius:6px; overflow:hidden;">
                <div id="render-progress-bar" style="height:100%; width:0%; background:linear-gradient(90deg,#8b5cf6,#f97316); transition:width 0.5s;"></div>
            </div>
            <span id="render-progress-text" style="color:#f8fafc; font-family:monospace; min-width:200px;">Iniciando...</span>
            <button onclick="this.parentElement.remove()" style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:1.2rem;">✕</button>
        `;
        document.body.appendChild(container);
        bar = document.getElementById('render-progress-bar');
    }
    
    if (renderPollInterval) clearInterval(renderPollInterval);
    
    renderPollInterval = setInterval(() => {
        fetch('https://api.apolloedit.com/api/render_status')
            .then(r => r.json())
            .then(s => {
                bar.style.width = s.progress + '%';
                document.getElementById('render-progress-text').innerText = s.message;
                
                if (s.state === 'done') {
                    clearInterval(renderPollInterval);
                    bar.style.background = '#22c55e'; // Verde = concluído
                    
                    // Envia para o Bagageiro!
                    if (window.apolloTransferOS) {
                        try {
                            const outputFileName = s.output_file ? s.output_file.split(/[\/\\]/).pop() : "timeline_final_render.mp4";
                            const fileUrl = `/api/download_video?path=` + encodeURIComponent(s.output_file || "timeline_final_render.mp4");
                            window.apolloTransferOS.addItem('video', outputFileName, 'Timeline Render', null, { url: fileUrl });
                            if (window.showToast) window.showToast("📥 Render concluído! Enviado para Área de Transferência!", "success");
                        } catch(e) {}
                    }

                    setTimeout(() => {
                        document.getElementById('render-progress-container')?.remove();
                    }, 4000);
                } else if (s.state === 'error') {
                    clearInterval(renderPollInterval);
                    bar.style.background = '#ef4444';
                }
            })
            .catch(() => clearInterval(renderPollInterval));
    }, 1000); // Atualiza a cada 1 segundo
}

// =============================================================
// ===   PARTE 8: POLIMENTO FINAL (Passo 20 do Roadmap)      ===
// =============================================================

// --- 12. THUMBNAIL REAL NA BIBLIOTECA ---
// Quando um card de mídia é adicionado, tenta carregar o frame do vídeo
function attachThumbToCard(div, path) {
    const thumbEl = div.querySelector('.media-thumb');
    if (!thumbEl) return;
    const img = document.createElement('img');
    img.src = `/api/thumb?path=${encodeURIComponent(path)}`;
    img.style.cssText = 'width:100%;height:100%;object-fit:cover;border-radius:4px;';
    img.onerror = () => {}; // Silencia se não conseguir (áudio, etc.)
    img.onload = () => {
        thumbEl.innerHTML = '';
        thumbEl.appendChild(img);
    };
}

// Aplicar thumb nos cards de exemplo existentes
document.querySelectorAll('.media-item[data-path]').forEach(div => {
    attachThumbToCard(div, div.dataset.path);
});

// --- 13. MENU DE CONTEXTO (CLIQUE DIREITO NO CLIPE) ---
let activeMenu = null;

function closeContextMenu() {
    if (activeMenu) { activeMenu.remove(); activeMenu = null; }
}

function showContextMenu(x, y, clip) {
    closeContextMenu();
    const menu = document.createElement('div');
    menu.className = 'context-menu';
    menu.innerHTML = `
        <div class="context-menu-item" id="ctx-duplicate">📋 Duplicar Clipe</div>
        <div class="context-menu-item" id="ctx-split">✂️ Cortar aqui (C)</div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" id="ctx-color-video" style="${clip.type!=='video'?'display:none':''}">🔵 Vídeo Principal</div>
        <div class="context-menu-item" id="ctx-color-broll" style="${clip.type!=='video'?'display:none':''}">🟣 B-Roll</div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item danger" id="ctx-delete">🗑️ Excluir Clipe (Del)</div>
    `;
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
    document.body.appendChild(menu);
    activeMenu = menu;

    menu.querySelector('#ctx-duplicate').onclick = () => {
        const trackEl = clip.element.parentElement;
        createClip(clip.name, clip.type, clip.start + clip.duration + 0.1, clip.duration, clip.color, trackEl, clip.trimIn);
        closeContextMenu();
    };

    menu.querySelector('#ctx-split').onclick = () => {
        if (State.currentTime > clip.start && State.currentTime < clip.start + clip.duration) {
            const cutPoint = State.currentTime;
            const origDur = clip.duration;
            clip.duration = cutPoint - clip.start;
            updateClipVisual(clip, clip.element);
            createClip(clip.name, clip.type, cutPoint, origDur - clip.duration, clip.color, clip.element.parentElement, clip.trimIn + clip.duration);
        }
        closeContextMenu();
    };

    const ctxColorVideo = menu.querySelector('#ctx-color-video');
    if (ctxColorVideo) ctxColorVideo.onclick = () => {
        clip.color = '#3b82f6'; clip.element.style.backgroundColor = '#3b82f6'; closeContextMenu();
    };

    const ctxColorBroll = menu.querySelector('#ctx-color-broll');
    if (ctxColorBroll) ctxColorBroll.onclick = () => {
        clip.color = '#8b5cf6'; clip.element.style.backgroundColor = '#8b5cf6'; closeContextMenu();
    };

    menu.querySelector('#ctx-delete').onclick = () => {
        const idx = State.clips.indexOf(clip);
        if (idx > -1) { State.selectedClip = null; clip.element.remove(); State.clips.splice(idx, 1); updateInspector(); }
        closeContextMenu();
    };
}

// Fechar menu ao clicar fora
document.addEventListener('click', closeContextMenu);
document.addEventListener('contextmenu', (e) => e.preventDefault());

// Listener global de contextmenu em TODOS os trilhos (dinâmicos incluídos)
document.getElementById('timeline-tracks').addEventListener('contextmenu', (e) => {
    e.preventDefault();
    const clipEl = e.target.closest('.timeline-clip');
    if (!clipEl) return;
    const clip = State.clips.find(c => c.element === clipEl);
    if (clip) showContextMenu(e.clientX, e.clientY, clip);
});

// --- 14. PAINEL DE ATALHOS FLUTUANTE ---
const btnShortcuts = document.createElement('button');
btnShortcuts.className = 'btn-shortcuts';
btnShortcuts.title = 'Atalhos de Teclado';
btnShortcuts.innerText = '⌨️';
document.body.appendChild(btnShortcuts);

let shortcutsVisible = false;
btnShortcuts.addEventListener('click', () => {
    shortcutsVisible = !shortcutsVisible;
    let panel = document.getElementById('shortcuts-panel');
    if (shortcutsVisible) {
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'shortcuts-panel';
            panel.className = 'shortcuts-panel';
            panel.innerHTML = `
                <h4>⌨️ Atalhos do Editor</h4>
                <div class="shortcut-row"><span>Play / Pause</span><span class="shortcut-key">Space</span></div>
                <div class="shortcut-row"><span>Ferramenta Seleção</span><span class="shortcut-key">V</span></div>
                <div class="shortcut-row"><span>Ferramenta Gilete</span><span class="shortcut-key">B</span></div>
                <div class="shortcut-row"><span>Cortar sob Playhead</span><span class="shortcut-key">C</span></div>
                <div class="shortcut-row"><span>Excluir clipe</span><span class="shortcut-key">Del</span></div>
                <div class="shortcut-row"><span>Exportar Timeline</span><span class="shortcut-key">Ctrl+E</span></div>
                <div class="shortcut-row"><span>Selecionar tudo</span><span class="shortcut-key">Ctrl+A</span></div>
                <div class="shortcut-row"><span>Desfazer</span><span class="shortcut-key">Ctrl+Z</span></div>
                <div class="shortcut-row"><span>Zoom +</span><span class="shortcut-key">+</span></div>
                <div class="shortcut-row"><span>Zoom -</span><span class="shortcut-key">-</span></div>
                <div class="shortcut-row"><span>Ir ao Início</span><span class="shortcut-key">Home</span></div>
                <div class="shortcut-row"><span>Ir ao Fim</span><span class="shortcut-key">End</span></div>
                <div class="shortcut-row"><span>Voltar ao modo Seleção</span><span class="shortcut-key">Esc</span></div>
            `;
            document.body.appendChild(panel);
        }
        panel.style.display = 'block';
    } else if (panel) {
        panel.style.display = 'none';
    }
});

// ================================================================
// === PASSO 13: ZONAS DE TRANSIÇÃO                            ===
// ================================================================

const TRANSITION_TYPES = {
    'fade':       { label: 'Fade',      icon: '🌅', ffmpeg: 'fade' },
    'dissolve':   { label: 'Dissolve',  icon: '💫', ffmpeg: 'dissolve' },
    'zoom-in':    { label: 'Zoom In',   icon: '🔍', ffmpeg: 'zoominzoomout' },
    'slide-left': { label: 'Slide ←',   icon: '⬅️', ffmpeg: 'slideleft' },
    'wipe':       { label: 'Wipe',      icon: '↔️', ffmpeg: 'wipeleft' },
};

let selectedTransition = null;

// Criar o bloco DOM da transição e posicioná-lo
function createTransitionBlock(leftClip, rightClip, type, duration) {
    // Evitar duplicata
    const existing = State.transitions.find(
        t => t.leftClipId === leftClip.id && t.rightClipId === rightClip.id
    );
    if (existing) { updateTransitionPosition(existing); return; }

    const transition = {
        id: State.nextId++,
        leftClipId: leftClip.id,
        rightClipId: rightClip.id,
        type,
        duration,
        element: null
    };

    const def = TRANSITION_TYPES[type] || TRANSITION_TYPES['fade'];
    const trackEl = leftClip.element.parentElement;

    const el = document.createElement('div');
    el.className = 'transition-block';
    el.dataset.transitionId = transition.id;
    el.innerHTML = `
        <div class="transition-block-inner">
            <span class="t-icon">${def.icon}</span>
            <span class="t-label">${def.label}</span>
            <span class="t-dur">${duration.toFixed(1)}s</span>
        </div>
    `;
    trackEl.appendChild(el);
    transition.element = el;
    State.transitions.push(transition);

    updateTransitionPosition(transition);

    // Clique → selecionar e abrir inspetor
    el.addEventListener('click', (e) => {
        e.stopPropagation();
        // Desselecionar anterior
        if (selectedTransition && selectedTransition.element) {
            selectedTransition.element.classList.remove('selected');
        }
        selectedTransition = transition;
        el.classList.add('selected');
        openTransitionInspector(transition);
    });

    // Duplo clique → mudar tipo rapidamente
    el.addEventListener('dblclick', (e) => {
        e.stopPropagation();
        showTransitionPicker(e.clientX, e.clientY, transition);
    });

    return transition;
}

// Atualizar a posição do bloco na timeline (chamado ao fazer zoom ou mover clips)
function updateTransitionPosition(transition) {
    const leftClip = State.clips.find(c => c.id === transition.leftClipId);
    const rightClip = State.clips.find(c => c.id === transition.rightClipId);
    if (!leftClip || !rightClip || !transition.element) return;

    const junctionTime = leftClip.start + leftClip.duration; // Momento da junção
    const halfDur = transition.duration / 2;

    const startPx = (junctionTime - halfDur) * State.zoomLevel + 80;
    const widthPx = Math.max(20, transition.duration * State.zoomLevel);

    transition.element.style.left = startPx + 'px';
    transition.element.style.width = widthPx + 'px';
}

// Atualizar TODAS as transições (chamado ao fazer zoom)
function updateAllTransitions() {
    State.transitions.forEach(updateTransitionPosition);
}

// Hook no zoomLevel — re-renderizar transições ao fazer zoom
UI.zoomSlider.addEventListener('input', () => updateAllTransitions());

// Modal de seleção de tipo de transição
function showTransitionPicker(x, y, transition) {
    document.getElementById('transition-picker')?.remove();
    const picker = document.createElement('div');
    picker.id = 'transition-picker';
    picker.style.cssText = `
        position: fixed; left: ${x}px; top: ${y}px;
        background: #1e293b; border: 1px solid #475569; border-radius: 8px;
        padding: 8px; z-index: 9999; min-width: 160px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); animation: fadeIn 0.1s ease;
    `;
    picker.innerHTML = `
        <div style="font-size:0.75rem;color:#94a3b8;padding:4px 8px 8px;border-bottom:1px solid #334155;margin-bottom:4px;">
            ✨ Tipo de Transição
        </div>
        ${Object.entries(TRANSITION_TYPES).map(([key, def]) => `
            <div class="context-menu-item" data-type="${key}">
                ${def.icon} ${def.label}
            </div>
        `).join('')}
        <div class="context-menu-divider"></div>
        <div style="padding:4px 8px;">
            <label style="font-size:0.7rem;color:#94a3b8;">Duração (s)</label>
            <input type="number" id="t-dur-input" min="0.2" max="5" step="0.1" value="${transition.duration}"
                style="width:100%;background:#0f172a;border:1px solid #334155;color:white;padding:3px 6px;border-radius:3px;font-size:0.8rem;margin-top:3px;">
        </div>
        <div style="display:flex;gap:4px;padding:6px 8px 2px;">
            <button id="t-apply" style="flex:1;background:#8b5cf6;border:none;color:white;padding:4px;border-radius:4px;cursor:pointer;font-size:0.75rem;">✔ Aplicar</button>
            <button id="t-remove" style="flex:1;background:#7f1d1d;border:none;color:#fca5a5;padding:4px;border-radius:4px;cursor:pointer;font-size:0.75rem;">🗑 Remover</button>
        </div>
    `;
    document.body.appendChild(picker);

    // Selecionar tipo
    picker.querySelectorAll('[data-type]').forEach(btn => {
        btn.addEventListener('click', () => {
            picker.querySelectorAll('[data-type]').forEach(b => b.style.background = '');
            btn.style.background = '#334155';
            transition.type = btn.dataset.type;
        });
    });

    // Aplicar
    picker.querySelector('#t-apply').onclick = () => {
        const dur = parseFloat(picker.querySelector('#t-dur-input').value) || 1.0;
        transition.duration = dur;
        const def = TRANSITION_TYPES[transition.type] || TRANSITION_TYPES['fade'];
        if (transition.element) {
            transition.element.querySelector('.t-icon').textContent = def.icon;
            transition.element.querySelector('.t-label').textContent = def.label;
            transition.element.querySelector('.t-dur').textContent = dur.toFixed(1) + 's';
            updateTransitionPosition(transition);
        }
        picker.remove();
        openTransitionInspector(transition);
    };

    // Remover
    picker.querySelector('#t-remove').onclick = () => {
        removeTransition(transition);
        picker.remove();
    };

    // Fechar ao clicar fora
    setTimeout(() => document.addEventListener('click', () => picker.remove(), { once: true }), 100);
}

function removeTransition(transition) {
    if (transition.element) transition.element.remove();
    const idx = State.transitions.indexOf(transition);
    if (idx > -1) State.transitions.splice(idx, 1);
    if (selectedTransition === transition) {
        selectedTransition = null;
        updateInspector();
    }
}

// Abre o inspetor de transição no painel lateral
function openTransitionInspector(transition) {
    const content = document.getElementById('inspector-content');
    const def = TRANSITION_TYPES[transition.type] || TRANSITION_TYPES['fade'];
    const leftClip = State.clips.find(c => c.id === transition.leftClipId);
    const rightClip = State.clips.find(c => c.id === transition.rightClipId);
    content.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:12px;">
            <div style="background:#1e293b;border-radius:8px;padding:10px;text-align:center;">
                <span style="font-size:2rem;">${def.icon}</span>
                <div style="font-weight:bold;color:#f59e0b;margin-top:4px;">${def.label}</div>
                <div style="font-size:0.7rem;color:#64748b;margin-top:2px;">Transição</div>
            </div>
            <label class="inspector-form">
                <span>Tipo de Transição</span>
                <select id="t-type-sel">
                    ${Object.entries(TRANSITION_TYPES).map(([k, d]) =>
                        `<option value="${k}" ${k === transition.type ? 'selected' : ''}>${d.icon} ${d.label}</option>`
                    ).join('')}
                </select>
            </label>
            <label class="inspector-form">
                <span>Duração (segundos)</span>
                <input type="number" id="t-dur-sel" min="0.2" max="5" step="0.1" value="${transition.duration}">
            </label>
            <div style="font-size:0.7rem;color:#64748b;">
                📎 ${leftClip?.name?.split(/[\\/]/).pop() ?? '?'} → ${rightClip?.name?.split(/[\\/]/).pop() ?? '?'}
            </div>
            <button id="t-apply-insp" style="background:#8b5cf6;border:none;color:white;padding:8px;border-radius:6px;cursor:pointer;font-weight:bold;">
                ✔ Aplicar
            </button>
            <button id="t-remove-insp" style="background:#7f1d1d;border:none;color:#fca5a5;padding:6px;border-radius:6px;cursor:pointer;">
                🗑 Remover Transição
            </button>
        </div>
    `;
    document.getElementById('t-apply-insp').onclick = () => {
        transition.type = document.getElementById('t-type-sel').value;
        transition.duration = parseFloat(document.getElementById('t-dur-sel').value) || 1.0;
        const d = TRANSITION_TYPES[transition.type];
        if (transition.element) {
            transition.element.querySelector('.t-icon').textContent = d.icon;
            transition.element.querySelector('.t-label').textContent = d.label;
            transition.element.querySelector('.t-dur').textContent = transition.duration.toFixed(1) + 's';
            updateTransitionPosition(transition);
        }
        openTransitionInspector(transition); // Atualiza
    };
    document.getElementById('t-remove-insp').onclick = () => removeTransition(transition);
}

// Adicionar botão "+" na borda direita de cada clipe ao criá-lo
function addTransitionButton(clip) {
    if (clip.type !== 'video') return; // Transições só em vídeo
    const addBtn = document.createElement('button');
    addBtn.className = 'transition-add-btn';
    addBtn.textContent = '+';
    addBtn.title = 'Adicionar Transição';
    addBtn.style.left = '100%';
    clip.element.appendChild(addBtn);

    addBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        // Encontrar o clipe mais próximo à direita na mesma trilha
        const trackEl = clip.element.parentElement;
        const clipsOnTrack = State.clips.filter(c =>
            c.element.parentElement === trackEl && c.type === 'video'
        ).sort((a, b) => a.start - b.start);

        const myIndex = clipsOnTrack.indexOf(clip);
        const nextClip = clipsOnTrack[myIndex + 1];

        if (!nextClip) {
            alert('Sem clipe à direita para adicionar transição.');
            return;
        }

        // Verificar adjacência (menos de 0.5s de gap)
        const gap = nextClip.start - (clip.start + clip.duration);
        if (gap > 0.5) {
            alert('Os clipes não são adjacentes. Coloque-os lado a lado primeiro.');
            return;
        }

        showTransitionPicker(e.clientX, e.clientY, { type: 'fade', duration: 1.0,
            apply: (type, dur) => createTransitionBlock(clip, nextClip, type, dur)
        });

        // Picker especial para novo (sem transition object ainda)
        const picker = document.getElementById('transition-picker');
        if (picker) {
            picker.querySelector('#t-apply').onclick = () => {
                const type = picker.querySelector('[data-type][style*="background"]')?.dataset.type || 'fade';
                const dur = parseFloat(picker.querySelector('#t-dur-input').value) || 1.0;
                createTransitionBlock(clip, nextClip, type, dur);
                picker.remove();
            };
        }
    });
}


// --- 15. ATALHOS EXTRAS DE TECLADO (somente atalhos não cobertos pelo listener principal) ---
window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;

    // Ctrl+E = Exportar
    if (e.ctrlKey && e.code === 'KeyE') {
        e.preventDefault();
        document.getElementById('btn-export')?.click();
    }

    // Ctrl+A = Selecionar todos os clipes
    if (e.ctrlKey && e.code === 'KeyA') {
        e.preventDefault();
        State.clips.forEach(c => c.element.classList.add('selected'));
        if (State.clips.length > 0) {
            State.selectedClip = State.clips[State.clips.length - 1];
            updateInspector();
        }
    }

    // Ctrl+Z = Desfazer via HistoryManager
    if (e.ctrlKey && e.code === 'KeyZ') {
        e.preventDefault();
        if (typeof HistoryManager !== 'undefined') HistoryManager.undo();
    }

    // Ctrl+Y = Refazer via HistoryManager
    if (e.ctrlKey && e.code === 'KeyY') {
        e.preventDefault();
        if (typeof HistoryManager !== 'undefined') HistoryManager.redo();
    }

    // + e - para Zoom
    if (e.code === 'Equal' || e.code === 'NumpadAdd') {
        const slider = document.getElementById('zoom-slider');
        if (slider) { slider.value = Math.min(50, parseInt(slider.value) + 2); slider.dispatchEvent(new Event('input')); }
    }
    if (e.code === 'Minus' || e.code === 'NumpadSubtract') {
        const slider = document.getElementById('zoom-slider');
        if (slider) { slider.value = Math.max(1, parseInt(slider.value) - 2); slider.dispatchEvent(new Event('input')); }
    }

    // Home = Voltar ao início
    if (e.code === 'Home') {
        State.currentTime = 0;
        updatePlayhead();
        if (UI.timeDisplay) UI.timeDisplay.innerText = formatTime(0);
    }

    // End = Ir para o fim do projeto
    if (e.code === 'End' && State.clips.length > 0) {
        State.currentTime = Math.max(...State.clips.map(c => c.start + c.duration));
        updatePlayhead();
        if (UI.timeDisplay) UI.timeDisplay.innerText = formatTime(State.currentTime);
    }

    // Escape = Volta para Seleção
    if (e.code === 'Escape') setActiveTool('select');
});

// ============================================================
// === PASSO 18: COPILOTO IA (CHAT E EDIÇÃO AUTOMÁTICA)     ===
// ============================================================

let chatHistory = [];

function switchInspectorTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    document.getElementById('tab-btn-' + tab).classList.add('active');
    document.getElementById(tab === 'chat' ? 'chat-panel' : 'inspector-content').classList.add('active');
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    appendChatMessage('user', msg);
    
    // Interceptar pedido de B-Roll / Imagem
    const brollMatch = msg.match(/^(?:crie|gere|b-roll|imagem|foto)\s+(.*)/i);
    if (brollMatch) {
        document.getElementById('chat-typing').style.display = 'block';
        document.getElementById('chat-typing').innerText = 'Gerando Imagem IA...';
        try {
            const response = await fetch('https://api.apolloedit.com/api/generate_broll', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: brollMatch[1] })
            });
            const data = await response.json();
            document.getElementById('chat-typing').style.display = 'none';
            document.getElementById('chat-typing').innerText = 'Pensando...';
            if (data.status === 'success') {
                appendChatMessage('copilot', `✅ Imagem gerada com sucesso! Adicionando à timeline...`);
                // Insert into highest video track (broll or v1)
                const trackEl = document.querySelector('.track[data-track-type="broll"] .track-content') || document.querySelector('.track[data-track-type="video"] .track-content');
                if (trackEl) {
                    createClip(data.image_path, 'video', State.currentTime, 5.0, '#3b82f6', trackEl);
                    if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
                }
            } else {
                appendChatMessage('copilot', '❌ Erro ao gerar imagem: ' + data.error);
            }
        } catch (e) {
            document.getElementById('chat-typing').style.display = 'none';
            document.getElementById('chat-typing').innerText = 'Pensando...';
            appendChatMessage('copilot', '❌ Falha de conexão ao gerar imagem.');
        }
        return;
    }

    document.getElementById('chat-typing').style.display = 'block';
    
    // Preparar estado simplificado da timeline
    const timelineState = {
        currentTime: State.currentTime,
        clips: State.clips.map(c => ({
            id: c.id,
            name: c.name,
            type: c.type,
            start: c.start,
            duration: c.duration,
            track: c.element.parentElement.closest('.track').dataset.trackId,
            scale: c.scale || 100,
            x: c.posX || 0,
            y: c.posY || 0
        }))
    };

    try {
        const isTurbo = window.ApolloEconomy && window.ApolloEconomy.hasCopilotTurbo();
        const typingEl = document.getElementById('chat-typing');
        
        if (!isTurbo) {
             typingEl.innerText = 'Processando em CPU Compartilhada...';
             typingEl.style.color = '#f59e0b';
        } else {
             typingEl.innerText = 'Pensando (T4 Dedicada)...';
             typingEl.style.color = '#10b981';
        }
        
        const response = await fetch('https://api.apolloedit.com/api/chat_copilot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg,
                timeline: timelineState,
                history: chatHistory
            })
        });

        const data = await response.json();
        
        // Atraso removido. O atraso será o real do processamento do backend na fila da máquina gratuita.
        
        document.getElementById('chat-typing').style.display = 'none';

        if (data.status === 'success') {
            const aiResponse = data.response || data;
            const messageText = aiResponse.message || data.reply;
            
            appendChatMessage('copilot', messageText);
            
            // Salva no historico local
            chatHistory.push({ role: 'user', text: msg });
            chatHistory.push({ role: 'copilot', text: messageText });
            if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);
            
            // Aplicar operações JSON
            if (aiResponse.operations && aiResponse.operations.length > 0) {
                applyCopilotOperations(aiResponse.operations);
            }
            if (data.actions) executeChatActions(data.actions);
            
            // O Upsell
            if (!isTurbo && Math.random() > 0.5) { // 50% de chance de mostrar o upsell
                 setTimeout(() => {
                     appendChatMessage('copilot', '⚡ *O seu Copiloto está rodando em modo Econômico. Assine o **Plano Pro** (Chip Turbo na Loja) para equipar seu Copiloto com um Chip Dedicado e ter respostas e geração de voz em Tempo Real.*');
                 }, 2000);
            }
        } else {
            appendChatMessage('copilot', '❌ Erro: ' + (data.message || 'Falha no processamento interno.'));
        }
    } catch (e) {
        document.getElementById('chat-typing').style.display = 'none';
        appendChatMessage('copilot', '❌ Falha de comunicação com o servidor.');
        console.error(e);
    }
}

function appendChatMessage(role, text) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'chat-msg ' + role;
    
    // Converte tags especiais em botões HTML (Botão Visualizador)
    const brollRegex = /\[GERAR_BROLL:\s*(.*?)\]/g;
    if (brollRegex.test(text)) {
        div.innerHTML = text.replace(brollRegex, (match, prompt) => {
            return `<button class="btn-purchase" style="margin-top:10px; padding:8px 15px; font-size:13px; display:block; width:100%; border-radius:6px; cursor:pointer;" onclick="window.triggerBRoll(this, '${prompt.replace(/'/g, "\\'")}')">🎨 Gerar Visualizador (FLUX)</button>`;
        });
    } else {
        div.innerHTML = text.replace(/\n/g, '<br>');
    }
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

window.triggerBRoll = function(btn, prompt) {
    btn.disabled = true;
    btn.innerText = "Processando no Motor Gráfico...";
    appendChatMessage('user', `[Comando] Gerar visualizador de: ${prompt}`);
    
    fetch('https://api.apolloedit.com/api/generate_broll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            btn.innerText = "✅ Gerado e Adicionado!";
            let trackContainer = document.querySelector('.track[data-track-type="broll"] .track-content');
            if (!trackContainer) trackContainer = addTrack('broll');
            createClip(data.image_path, 'image', State.currentTime, 5.0, '#3b82f6', trackContainer);
            if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
            appendChatMessage('copilot', `Pronto! A imagem foi renderizada pelas nossas GPUs Cloud e adicionada à sua Timeline na posição ${State.currentTime}s.`);
        } else {
            btn.innerText = "❌ Falha no Render";
            btn.disabled = false;
            appendChatMessage('copilot', '❌ Erro ao gerar imagem: ' + data.error);
        }
    })
    .catch(err => {
        btn.innerText = "❌ Falha de Rede";
        btn.disabled = false;
        appendChatMessage('copilot', '❌ Erro de conexão com os servidores na nuvem.');
    });
}

function applyCopilotOperations(ops) {
    ops.forEach(op => {
        try {
            if (op.type === 'add_clip') {
                // Encontrar a trilha correta ou criar se não existir
                let trackContainer = document.getElementById('track-' + op.track + '-content');
                if (!trackContainer) {
                    // Tenta criar
                    if (op.track.startsWith('v')) trackContainer = addTrack('broll');
                    else trackContainer = addTrack('audio-music');
                }
                const color = op.clip_type === 'video' ? '#8b5cf6' : '#f97316';
                createClip(op.path, op.clip_type, op.start, op.duration, color, trackContainer);
            }
            else if (op.type === 'remove_clip') {
                const clip = State.clips.find(c => String(c.id) === String(op.id));
                if (clip) {
                    clip.element.remove();
                    State.clips = State.clips.filter(c => c.id !== clip.id);
                    if (State.selectedClip === clip) {
                        State.selectedClip = null;
                        updateInspector();
                    }
                }
            }
            else if (op.type === 'update_clip') {
                const clip = State.clips.find(c => String(c.id) === String(op.id));
                if (clip && op.properties) {
                    if (op.properties.scale !== undefined) clip.scale = op.properties.scale;
                    if (op.properties.x !== undefined) clip.posX = op.properties.x;
                    if (op.properties.y !== undefined) clip.posY = op.properties.y;
                    if (op.properties.volume !== undefined) clip.volume = op.properties.volume;
                    if (State.selectedClip === clip) updateInspector();
                }
            }
            else if (op.type === 'set_ratio') {
                State.projectRatio = op.ratio || '16:9';
                if (typeof applyProjectRatio === 'function') applyProjectRatio();
            }
            else if (op.type === 'split_clip') {
                const clip = State.clips.find(c => String(c.id) === String(op.id));
                if (clip && op.time) {
                    splitClipAtTime(clip, parseFloat(op.time));
                }
            }
            else if (op.type === 'clear_timeline') {
                State.clips.forEach(c => c.element.remove());
                State.clips = [];
                State.selectedClip = null;
                updateInspector();
            }
            else if (op.type === 'auto_reportage') {
                const btn = document.getElementById('btn-ai-edit');
                if (btn) {
                    appendChatMessage('copilot', '🎬 Iniciando o Diretor Autônomo. Isso pode levar alguns minutos...');
                    btn.click();
                } else {
                    appendChatMessage('copilot', '❌ Botão Auto-Edit não encontrado.');
                }
            }
            else if (op.type === 'generate_broll_image') {
                appendChatMessage('copilot', `🎨 Gerando imagem: "${op.prompt}"...`);
                fetch('https://api.apolloedit.com/api/generate_broll', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: op.prompt })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        let trackContainer = document.getElementById('track-' + op.track + '-content');
                        if (!trackContainer) trackContainer = addTrack('broll');
                        createClip(data.path, 'image', op.start, 3.0, '#38bdf8', trackContainer);
                        appendChatMessage('copilot', '✅ Imagem B-Roll adicionada à timeline!');
                        if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
                    } else {
                        appendChatMessage('copilot', '❌ Erro ao gerar imagem: ' + data.message);
                    }
                })
                .catch(err => {
                    appendChatMessage('copilot', '❌ Erro de conexão ao gerar imagem.');
                });
            }
        } catch (err) {
            console.error("Erro ao aplicar operação da IA:", op, err);
        }
    });
    if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
}




// =============================================================
// === LÓGICA DE PROPORÇÃO INTELIGENTE (ASPECT RATIO)        ===
// =============================================================
const ratioSelect = document.getElementById('project-ratio');
if (ratioSelect) {
    ratioSelect.addEventListener('change', (e) => {
        State.projectRatio = e.target.value;
        applyProjectRatio();
    });
}

function applyProjectRatio() {
    const player = document.getElementById('main-player');
    if (!player) return;
    
    // Reset classes
    player.className = '';
    if (ratioSelect) ratioSelect.value = State.projectRatio;
    
    let ratio = State.projectRatio;
    
    if (ratio === 'auto') {
        // Procura o primeiro vídeo na timeline
        const firstVideo = State.clips.find(c => c.type === 'video');
        if (firstVideo && firstVideo.width && firstVideo.height) {
            if (firstVideo.height > firstVideo.width) ratio = '9:16';
            else if (firstVideo.height === firstVideo.width) ratio = '1:1';
            else ratio = '16:9';
        } else {
            ratio = '16:9'; // Padrão de segurança
        }
    }
    
    if (ratio === '16:9') player.classList.add('ratio-horizontal');
    else if (ratio === '9:16') player.classList.add('ratio-vertical');
    else if (ratio === '1:1') player.classList.add('ratio-square');
}


// ============================================================
// === PASSO 19: HISTORY E MENU DE CONTEXTO                 ===
// ============================================================

// --- SISTEMA DE HISTÓRICO (UNDO/REDO) ---
const HistoryManager = {
    history: [],
    currentIndex: -1,
    isRestoring: false,

    saveState() {
        if (this.isRestoring) return;
        if (this.currentIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentIndex + 1);
        }
        
        const stateSnapshot = State.clips.map(c => ({
            id: c.id, name: c.name, type: c.type, start: c.start, 
            duration: c.duration, trimIn: c.trimIn, color: c.color,
            width: c.width, height: c.height,
            volume: c.volume, opacity: c.opacity,
            textContent: c.textContent, fontSize: c.fontSize, fontColor: c.fontColor,
            posX: c.posX, posY: c.posY, scale: c.scale,
            trackId: c.element?.parentElement?.closest('.track')?.dataset?.trackId
        }));
        
        this.history.push({ clips: stateSnapshot, currentTime: State.currentTime });
        if (this.history.length > 50) {
            this.history.shift();
            // currentIndex stays the same — it already points to the last entry after shift
        } else {
            this.currentIndex++;
        }
    },

    restoreState(index) {
        if (index < 0 || index >= this.history.length) return;
        this.isRestoring = true;
        this.currentIndex = index;
        const snapshot = this.history[index];
        
        State.clips.forEach(c => c.element.remove());
        State.clips = [];
        State.selectedClip = null;
        updateInspector();
        
        snapshot.clips.forEach(c => {
            const trackEl = document.getElementById(c.trackId + '-content') || document.getElementById('track-v1-content');
            if (trackEl) {
                createClip(c.name, c.type, c.start, c.duration, c.color, trackEl, c.trimIn, c.width, c.height);
                const newClip = State.clips[State.clips.length - 1];
                newClip.id = c.id;
                if (c.id >= State.nextId) State.nextId = c.id + 1;
            }
        });
        
        State.currentTime = snapshot.currentTime;
        updatePlayhead();
        if (UI.timeDisplay) UI.timeDisplay.innerText = formatTime(State.currentTime);
        this.isRestoring = false;
    },

    undo() {
        if (this.currentIndex > 0) this.restoreState(this.currentIndex - 1);
    },

    redo() {
        if (this.currentIndex < this.history.length - 1) this.restoreState(this.currentIndex + 1);
    }
};

window.addEventListener('keydown', (e) => {
    // Avoid triggering while typing in inputs (like chat)
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    if (e.ctrlKey && e.key.toLowerCase() === 'z' && !e.shiftKey) {
        e.preventDefault();
        HistoryManager.undo();
    } else if ((e.ctrlKey && e.key.toLowerCase() === 'y') || (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'z')) {
        e.preventDefault();
        HistoryManager.redo();
    }
});

setTimeout(() => HistoryManager.saveState(), 1000);

let isSnappingEnabled = true;
function toggleSnapping() {
    isSnappingEnabled = !isSnappingEnabled;
    const btn = document.getElementById('tool-btn-magnet');
    if (btn) {
        if (isSnappingEnabled) btn.classList.add('active');
        else btn.classList.remove('active');
    }
}

// --- MENU DE CONTEXTO ---
const ctxMenu = document.getElementById('context-menu');
let ctxClip = null;

if (ctxMenu) {
    document.getElementById('timeline-tracks').addEventListener('contextmenu', (e) => {
        e.preventDefault();
        const clipEl = e.target.closest('.timeline-clip');
        if (clipEl) {
            const clipId = State.clips.find(c => c.element === clipEl)?.id;
            ctxClip = State.clips.find(c => c.id === clipId);
            
            if (ctxClip) {
                State.clips.forEach(c => c.element.classList.remove('selected'));
                ctxClip.element.classList.add('selected');
                State.selectedClip = ctxClip;
                updateInspector();
            }

            ctxMenu.style.display = 'block';
            ctxMenu.style.left = e.pageX + 'px';
            ctxMenu.style.top = e.pageY + 'px';
        } else {
            ctxMenu.style.display = 'none';
            ctxClip = null;
        }
    });

    document.addEventListener('click', (e) => {
        if (ctxMenu && !e.target.closest('#context-menu')) {
            ctxMenu.style.display = 'none';
        }
    });

    const btnDelete = document.getElementById('ctx-delete');
    if (btnDelete) {
        btnDelete.addEventListener('click', () => {
            if (ctxClip) {
                const idx = State.clips.indexOf(ctxClip);
                if (idx > -1) {
                    ctxClip.element.remove();
                    State.clips.splice(idx, 1);
                    if (State.selectedClip === ctxClip) {
                        State.selectedClip = null;
                        updateInspector();
                    }
                    HistoryManager.saveState();
                }
            }
            ctxMenu.style.display = 'none';
        });
    }

    const btnDup = document.getElementById('ctx-duplicate');
    if (btnDup) {
        btnDup.addEventListener('click', () => {
            if (ctxClip) {
                const trackEl = ctxClip.element.parentElement;
                createClip(ctxClip.name, ctxClip.type, ctxClip.start + ctxClip.duration, ctxClip.duration, ctxClip.color, trackEl, ctxClip.trimIn, ctxClip.width, ctxClip.height);
                HistoryManager.saveState();
            }
            ctxMenu.style.display = 'none';
        });
    }

    const btnSplit = document.getElementById('ctx-split');
    if (btnSplit) {
        btnSplit.addEventListener('click', () => {
            if (ctxClip) {
                const splitResult = splitClipAtTime(ctxClip, State.currentTime);
                if (splitResult && typeof HistoryManager !== 'undefined') HistoryManager.saveState();
            }
            ctxMenu.style.display = 'none';
        });
    }

    const btnProp = document.getElementById('ctx-properties');
    if (btnProp) {
        btnProp.addEventListener('click', () => {
            if (typeof switchInspectorTab === 'function') switchInspectorTab('properties');
            ctxMenu.style.display = 'none';
        });
    }
}

// --- FERRAMENTA DE TEXTO ---
function addTextClip() {
    const trackElement = document.getElementById('track-t1-content');
    if (!trackElement) {
        alert("Trilha de texto T1 não encontrada!");
        return;
    }
    const color = '#ec4899'; // Rosa para textos
    const clip = createClip('Novo Texto', 'text', State.currentTime, 3.0, color, trackElement);
    clip.textContent = "MEU TEXTO IA";
    clip.fontSize = 72;
    clip.fontColor = "#ffffff";
    clip.posX = 0;
    clip.posY = 0;
    
    // Atualiza nome na timeline
    clip.element.querySelector('strong').innerText = clip.textContent;
    
    State.selectedClip = clip;
    updateInspector();
    if (typeof HistoryManager !== 'undefined') HistoryManager.saveState();
}

// --- INBOX POLLER: Verifica se há mídias enviadas via /api/send_to_timeline ---
setInterval(() => {
    fetch('https://api.apolloedit.com/api/check_inbox')
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success' && data.files && data.files.length > 0) {
                data.files.forEach(path => {
                    const name = path.split('/').pop().split('\\').pop();
                    fetch(`/api/probe_file?path=${encodeURIComponent(path)}`)
                        .then(r => r.json())
                        .then(probe => {
                            const realDuration = probe.status === 'success' ? probe.duration : 10.0;
                            let isVideo = false;
                            if (probe.status === 'success') {
                                isVideo = probe.has_video;
                            } else {
                                const ext = path.split('.').pop().toLowerCase();
                                isVideo = ['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(ext);
                            }
                            const grid = document.getElementById('media-grid');
                            const div = document.createElement('div');
                            div.className = 'media-item';
                            div.draggable = true;
                            div.dataset.type = isVideo ? 'video' : 'audio';
                            div.dataset.duration = realDuration;
                            div.dataset.path = path;
                            
                            const durStr = realDuration >= 60
                                ? `${Math.floor(realDuration/60)}m${(realDuration%60).toFixed(0)}s`
                                : `${realDuration.toFixed(1)}s`;
                            
                            div.innerHTML = `
                                <div class="media-thumb ${isVideo ? 'bg-blue' : 'bg-orange'}">${isVideo ? '🎥' : '🎵'}</div>
                                <div class="media-info" style="font-size:0.7rem; word-break:break-all;">${name}<br><span style="color:#00ff00; font-weight:bold;">NOVO! ${durStr}</span></div>
                            `;
                            
                            div.addEventListener('dragstart', (e) => {
                                e.dataTransfer.setData('text/plain', JSON.stringify({
                                    type: div.dataset.type,
                                    duration: realDuration,
                                    name: path,
                                    color: isVideo ? '#3b82f6' : '#f97316',
                                    width: probe.width || 0,
                                    height: probe.height || 0
                                }));
                                e.dataTransfer.effectAllowed = 'copy';
                            });
                            
                            grid.appendChild(div);
                            
                            // Exibe um aviso visual para o usuário
                            const msg = document.createElement('div');
                            msg.innerText = `Nova Mídia Recebida: ${name}`;
                            msg.style.cssText = "position:fixed; top:20px; right:20px; background:#2ED573; color:#1e1e1e; padding:10px 20px; border-radius:5px; z-index:9999; font-weight:bold; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: opacity 0.5s;";
                            document.body.appendChild(msg);
                            setTimeout(() => {
                                msg.style.opacity = '0';
                                setTimeout(() => msg.remove(), 500);
                            }, 4000);
                        });
                });
            }
        })
        .catch(err => console.error("Erro ao checar inbox:", err));
}, 3000);
