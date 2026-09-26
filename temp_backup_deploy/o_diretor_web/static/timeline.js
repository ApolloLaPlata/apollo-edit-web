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
    activeTool: 'select'
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

// Hover no modo Gilete — mostrar a linha de preview de corte
function setupRazorHover(trackContent) {
    trackContent.addEventListener('mousemove', (e) => {
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

        const line = getRazorLine();
        if (clipUnder) {
            // Posição X relativa ao timeline-tracks (incluindo scroll)
            const xInContainer = e.clientX - containerRect.left + tracksContainer.scrollLeft;
            line.style.left = xInContainer + 'px';
            line.style.display = 'block';
            document.getElementById('razor-line-label').textContent = formatTime(cutTime);
        } else {
            line.style.display = 'none';
        }
    });

    trackContent.addEventListener('mouseleave', () => {
        if (razorLine) razorLine.style.display = 'none';
    });

    // Clique no modo Gilete
    trackContent.addEventListener('click', (e) => {
        if (State.activeTool !== 'razor') return;
        e.stopPropagation();

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
            splitClipAtTime(clipUnder, cutTime);
        } else {
            // Clicar numa área vazia move o playhead e corta tudo que estiver na posição
            State.currentTime = cutTime;
            updatePlayhead();
            splitAllClipsAtPlayhead();
        }
    });
}


// --- 4. ENGINE DE CLIPES ---
function createClip(name, type, startTime, duration, color, trackElement, trimIn = 0.0) {
    const clip = {
        id: State.nextId++,
        name: name,
        type: type, // 'video' ou 'audio'
        start: startTime, // Onde começa na timeline
        duration: duration,
        trimIn: trimIn, // Onde começa dentro do arquivo original
        color: color,
        element: null
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

        // Lógica de Seleção (Passo 14)
        State.clips.forEach(c => c.element.classList.remove('selected'));
        clip.element.classList.add('selected');
        State.selectedClip = clip;
        updateInspector();
    });

    window.addEventListener('mousemove', (e) => {
        if (!mode) return;
        
        const deltaX = e.clientX - startX;
        const deltaSeconds = deltaX / State.zoomLevel;
        
        if (mode === 'move') {
            let newStart = initialStart + deltaSeconds;
            if (newStart < 0) newStart = 0;
            clip.start = newStart;
        } 
        else if (mode === 'trim-right') {
            let newDuration = initialDuration + deltaSeconds;
            if (newDuration < 0.5) newDuration = 0.5; // Mínimo 0.5s
            clip.duration = newDuration;
        }
        else if (mode === 'trim-left') {
            let newStart = initialStart + deltaSeconds;
            let newDuration = initialDuration - deltaSeconds;
            let newTrimIn = initialTrimIn + deltaSeconds;
            
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
            clip.start = newStart;
            clip.duration = newDuration;
            clip.trimIn = newTrimIn;
        }
        
        updateClipVisual(clip, clip.element);
        updateInspector(); // Atualiza painel dinamicamente
    });

    window.addEventListener('mouseup', () => {
        if (mode) {
            mode = null;
            clip.element.style.zIndex = '';
        }
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
    
    // Só troca o src se mudou de clipe
    if (previewCurrentClipId !== videoClip.id) {
        previewCurrentClipId = videoClip.id;
        mainPlayer.src = videoClip.name.startsWith('http') 
            ? videoClip.name 
            : `file:///${videoClip.name.replace(/\\/g, '/')}`;
        mainPlayer.load();
    }
    
    // Sincroniza o tempo interno do vídeo com a posição relativa dentro do clipe
    const clipLocalTime = (State.currentTime - videoClip.start) + (videoClip.trimIn || 0);
    
    // Só corrige se estiver mais de 0.3s fora de sync (evita loop de correção)
    if (Math.abs(mainPlayer.currentTime - clipLocalTime) > 0.3) {
        mainPlayer.currentTime = clipLocalTime;
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
                <button class="btn-track-solo btn-icon" title="Solo" data-track-id="${trackId}">S</button>
                <button class="btn-track-vis btn-icon" title="Ocultar" data-track-id="${trackId}">👁️</button>
                <button class="btn-icon" title="Remover trilha" onclick="this.closest('.track').remove(); delete State.tracks['${trackId}']">🗑️</button>
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
        const data = JSON.parse(e.dataTransfer.getData('text/plain'));
        const trackRect = track.getBoundingClientRect();
        const dropX = e.clientX - trackRect.left + track.scrollLeft;
        let startTime = Math.max(0, dropX / State.zoomLevel);
        createClip(data.name, data.type, startTime, data.duration, data.color, track);
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
                audioEl.src = `file:///${clip.name.replace(/\\/g, '/')}`;
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
        </div>
    `;

    // Conectar eventos (binding)
    const setVal = (id, field) => {
        const el = document.getElementById(id);
        const disp = document.getElementById(id + '-val');
        if (!el) return;
        el.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            c[field] = val;
            if (disp) disp.innerText = val + (field==='posX'||field==='posY'?'px':'%');
            
            // Para preview imediato no player HTML (opcional, só de volume e opacidade para videos simples)
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
    // Espaço para Play/Pause
    if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        togglePlay();
    }
    
    // Deletar clipe
    if ((e.code === 'Delete' || e.code === 'Backspace') && State.selectedClip && e.target.tagName !== 'INPUT') {
        const idx = State.clips.indexOf(State.selectedClip);
        if (idx > -1) {
            State.selectedClip.element.remove();
            State.clips.splice(idx, 1);
            State.selectedClip = null;
            updateInspector();
        }
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
            pos_y: c.posY !== undefined ? c.posY : 0
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
function sendToPython(draftMode = false) {
    const exportData = serializeProject();
    exportData.draft_mode = draftMode;

    fetch('/api/export_timeline', {
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
document.getElementById('btn-export').addEventListener('click', () => sendToPython(false));

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
        fetch('/api/browse_file')
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success' && data.path) {
                    const path = data.path;
                    const name = path.split('/').pop().split('\\').pop();
                    
                    // Usa FFprobe para ler a duração REAL do arquivo
                    fetch(`/api/probe_file?path=${encodeURIComponent(path)}`)
                        .then(r => r.json())
                        .then(probe => {
                            const realDuration = probe.status === 'success' ? probe.duration : 10.0;
                            const isVideo = probe.has_video;
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
                                    color: isVideo ? '#3b82f6' : '#f97316'
                                }));
                                e.dataTransfer.effectAllowed = 'copy';
                            });
                            
                            grid.appendChild(div);
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
        fetch('/api/render_status')
            .then(r => r.json())
            .then(s => {
                bar.style.width = s.progress + '%';
                document.getElementById('render-progress-text').innerText = s.message;
                
                if (s.state === 'done') {
                    clearInterval(renderPollInterval);
                    bar.style.background = '#22c55e'; // Verde = concluído
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


// --- 15. ATALHOS EXTRAS DE TECLADO ---
window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;

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

    // Ctrl+Z = Desfazer (remove o último clipe adicionado)
    if (e.ctrlKey && e.code === 'KeyZ') {
        e.preventDefault();
        const last = State.clips[State.clips.length - 1];
        if (last) {
            last.element.remove();
            State.clips.pop();
            if (State.selectedClip === last) { State.selectedClip = null; updateInspector(); }
        }
    }

    // + e - para Zoom
    if (e.code === 'Equal' || e.code === 'NumpadAdd') {
        const slider = document.getElementById('zoom-slider');
        slider.value = Math.min(50, parseInt(slider.value) + 2);
        slider.dispatchEvent(new Event('input'));
    }
    if (e.code === 'Minus' || e.code === 'NumpadSubtract') {
        const slider = document.getElementById('zoom-slider');
        slider.value = Math.max(1, parseInt(slider.value) - 2);
        slider.dispatchEvent(new Event('input'));
    }

    // Home = Voltar ao início
    if (e.code === 'Home') {
        State.currentTime = 0;
        updatePlayhead();
        UI.timeDisplay.innerText = formatTime(0);
    }

    // End = Ir para o fim do projeto
    if (e.code === 'End' && State.clips.length > 0) {
        State.currentTime = Math.max(...State.clips.map(c => c.start + c.duration));
        updatePlayhead();
        UI.timeDisplay.innerText = formatTime(State.currentTime);
    }

    // === Passo 12: Atalhos da Gilete ===
    // Space = Play/Pause (registrado no engine)
    if (e.code === 'Space') {
        e.preventDefault();
        togglePlay();
    }
    // V = Ferramenta de Seleção
    if (e.code === 'KeyV') setActiveTool('select');
    // B = Gilete (Blade/Razor)
    if (e.code === 'KeyB') setActiveTool('razor');
    // Escape = Volta para Seleção
    if (e.code === 'Escape') setActiveTool('select');
    // C = Cortar todos os clipes sob o playhead (modo rápido, sem mudar de ferramenta)
    if (e.code === 'KeyC' && !e.ctrlKey) splitAllClipsAtPlayhead();
    // Delete/Backspace = Excluir clipe selecionado
    if ((e.code === 'Delete' || e.code === 'Backspace') && State.selectedClip) {
        const idx = State.clips.indexOf(State.selectedClip);
        if (idx > -1) {
            State.selectedClip.element.remove();
            State.clips.splice(idx, 1);
            State.selectedClip = null;
            updateInspector();
        }
    }
});
