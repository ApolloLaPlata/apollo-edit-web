// ============================================================
// APOLLO VISUAL STUDIO v2.0 — Editor de Templates
// Camadas FIXAS: salva path + posição. Borda sólida.
// Camadas VARIÁVEIS: só salva posição/tamanho. Borda tracejada.
// Thumbnails para TODOS os layers (imagem ou frame de vídeo).
// ============================================================

const LAYERS_DEFAULT = [
    { id: 'lay0_bg',       title: '0. Background (Fundo)',    zIndex: 0, color: '#3b82f6', isFixed: true,  isFullscreen: true,  hasChroma: false, hasSortear: true  },
    { id: 'lay1_fundo',    title: '1. Vídeo Base (Notícia)',  zIndex: 1, color: '#f59e0b', isFixed: false, isFullscreen: false, hasChroma: false, hasSortear: true,  defaultW: 1080, defaultH: 1920, defaultX: 0,  defaultY: 0   },
    { id: 'lay2_narrador', title: '2. Narrador (Loop)',       zIndex: 2, color: '#ef4444', isFixed: false, isFullscreen: false, hasChroma: true,  hasSortear: true,  defaultW: 324,  defaultH: 576,  defaultX: 50, defaultY: 1344 },
    { id: 'lay3_frente',   title: '3. Tag / Frente',          zIndex: 3, color: '#8b5cf6', isFixed: false, isFullscreen: false, hasChroma: true,  hasSortear: true,  defaultW: 324,  defaultH: 576,  defaultX: 50, defaultY: 1344 },
    { id: 'lay4_extra',    title: '4. Elemento Extra/Top',    zIndex: 4, color: '#ec4899', isFixed: false, isFullscreen: false, hasChroma: true,  hasSortear: true,  defaultW: 540,  defaultH: 540,  defaultX: 50, defaultY: 50  },
];

let layersData   = {};
let layersDefs   = [];
let currentZoom  = 0.35;
let extraCount   = 0;
let currentFormat = 'vertical';

function getBaseWH() {
    return currentFormat === 'horizontal'
        ? { W: 1920, H: 1080 }
        : { W: 1080, H: 1920 };
}

// ── AUTO-SAVE (BACKUP)
function autoSave() {
    if (layersDefs.length > 0) {
        const state = { defs: layersDefs, data: layersData, extraCount, currentFormat };
        localStorage.setItem('apollo_autosave', JSON.stringify(state));
    }
}

function restoreAutoSave() {
    const saved = localStorage.getItem('apollo_autosave');
    if (saved) {
        try {
            const state = JSON.parse(saved);
            if (state.defs && state.data) {
                layersDefs = state.defs;
                layersData = state.data;
                extraCount = state.extraCount || 0;
                currentFormat = state.currentFormat || 'vertical';
                
                // Dispara o toast visual de aviso
                const toast = document.createElement('div');
                toast.innerText = '💾 Sessão recuperada com sucesso!';
                toast.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#10b981;color:#fff;padding:8px 16px;border-radius:20px;z-index:99999;font-weight:bold;box-shadow:0 4px 12px rgba(0,0,0,0.5);';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);
                
                return true;
            }
        } catch(e) {}
    }
    return false;
}

// ── INICIALIZAÇÃO
function init() {
    const restored = restoreAutoSave();
    if (!restored) {
        layersDefs = LAYERS_DEFAULT.map(l => ({ ...l }));
    }
    
    // Atualiza o rádio do formato
    const formatRadio = document.querySelector(`input[name="canvas_format"][value="${currentFormat}"]`);
    if (formatRadio) formatRadio.checked = true;

    renderAll();
    setupCanvasControls();
    setupToolbar();
    setTimeout(loadProfileList, 500);

    // Se restaurou, tenta recarregar os thumbnails salvos
    if (restored) {
        setTimeout(() => {
            layersDefs.forEach(l => {
                if (layersData[l.id]?.path) loadThumb(l.id);
            });
        }, 1000);
    }

    // Liga o Auto-Save a cada 5 segundos
    setInterval(autoSave, 5000);

    // Centralizar o Canvas no meio do espaço virtual (pan infinito)
    setTimeout(() => {
        const cw = document.querySelector('.canvas-wrapper');
        if (cw) {
            cw.scrollLeft = 4000 - cw.clientWidth / 2;
            cw.scrollTop  = 4000 - cw.clientHeight / 2;
        }
    }, 100);
}

// ── RENDERIZA SIDEBAR + CANVAS COMPLETO
function renderAll() {
    const sidebar = document.getElementById('layers-container');
    const canvas  = document.getElementById('render-canvas');
    sidebar.innerHTML = '';
    [...canvas.querySelectorAll('.layer-box')].forEach(b => b.remove());

    layersDefs.forEach(l => {
        if (!layersData[l.id]) initLayerData(l);
        renderSidebarCard(l, sidebar);
        renderCanvasBox(l, canvas);
    });
    updateAllBoxes();
}

function initLayerData(l) {
    const { W, H } = getBaseWH();
    layersData[l.id] = {
        path:    '',
        visible: true,
        chroma:  false,
        random:  false,
        locked:  false, // ← Trava de segurança
        x:  l.defaultX ?? 0,
        y:  l.defaultY ?? 0,
        w:  l.defaultW ?? W,
        h:  l.defaultH ?? H,
    };
}

// ── TOGGLE LOCK (Cadeado)
window.toggleLock = function(id) {
    const d = layersData[id];
    d.locked = !d.locked;
    const btn = document.getElementById(`btn_lock_${id}`);
    if (btn) btn.innerText = d.locked ? '🔒' : '🔓';
    const box = document.getElementById(`box_${id}`);
    if (box) {
        // Se travado, ignora clicks no canvas
        box.style.pointerEvents = d.locked ? 'none' : 'auto';
        box.style.opacity = d.locked ? '0.8' : '1';
    }
    const cardInputs = document.querySelectorAll(`#card_${id} input[type="number"]`);
    cardInputs.forEach(i => i.disabled = d.locked);
};

// ── CARD DA SIDEBAR
function renderSidebarCard(l, sidebar) {
    const d = layersData[l.id];
    const borderStyle = l.isFixed ? '3px solid #3b82f6' : '3px dashed #f59e0b';
    const badge = l.isFixed
        ? `<span class="badge fixed">FIXO</span>`
        : `<span class="badge variable">VARIÁVEL</span>`;
    const varNote = !l.isFixed
        ? `<div style="background:#1a1a2e;padding:4px 8px;border-radius:4px;font-size:0.76rem;color:#f59e0b;margin-bottom:4px;">
               ⚡ Variável — apenas posição e tamanho são salvos no perfil.
           </div>` : '';

    const card = document.createElement('div');
    card.className = 'layer-card';
    card.id = `card_${l.id}`;
    card.style.borderLeft = borderStyle;

    // Botões de reordenação
    const canReorder = !l.isFullscreen;
    const reorderBtns = canReorder ? `
        <div style="display:flex;flex-direction:column;gap:1px;margin-left:4px;">
            <button onclick="moveLayerUp('${l.id}')"   style="background:#334155;border:none;color:#fff;cursor:pointer;padding:1px 4px;border-radius:2px;font-size:10px;" title="Mover para frente">▲</button>
            <button onclick="moveLayerDown('${l.id}')" style="background:#334155;border:none;color:#fff;cursor:pointer;padding:1px 4px;border-radius:2px;font-size:10px;" title="Mover para trás">▼</button>
        </div>` : '';

    const titleHtml = l.isExtra 
        ? `<input type="text" value="${l.title}" onchange="renameLayer('${l.id}', this.value)" style="background:transparent;border:none;color:#fff;font-weight:600;font-size:1rem;border-bottom:1px solid #475569;outline:none;width:150px;font-family:inherit;">`
        : `<span style="color:#fff;font-weight:600;">${l.title}</span>`;

    card.innerHTML = `
        <div class="layer-header">
            <label style="display:flex;align-items:center;gap:6px;cursor:pointer;">
                <input type="checkbox" id="vis_${l.id}" ${d.visible ? 'checked' : ''}>
                ${titleHtml}
            </label>
            <div style="display:flex;align-items:center;gap:4px;">
                ${badge}
                ${!l.isFullscreen ? `<button onclick="toggleLock('${l.id}')" id="btn_lock_${l.id}" style="background:transparent;border:none;cursor:pointer;font-size:14px;" title="Travar Posição">🔓</button>` : ''}
                <div style="width:14px;height:14px;background:${l.color};border-radius:3px;"></div>
                ${reorderBtns}
            </div>
        </div>

        ${varNote}

        <div class="input-group">
            <label>Arquivo / Pasta:</label>
            <div style="display:flex;gap:4px;align-items:center;">
                <input type="text" id="path_${l.id}" placeholder="Caminho do arquivo..." value="${d.path}" style="flex:1;" oninput="onPathInput('${l.id}')">
                <button onclick="browseFile('${l.id}')" class="btn-mini" title="Procurar arquivo">📁</button>
                <button onclick="loadThumb('${l.id}')" class="btn-mini" title="Carregar preview no canvas">👁</button>
            </div>
            ${l.isFixed ? '' : '<div style="font-size:0.72rem;color:#64748b;margin-top:2px;">Preview apenas — path não salvo no perfil.</div>'}
        </div>

        ${!l.isFullscreen ? `
        <div class="layer-controls">
            <div><label>X (px)</label><input type="number" id="x_${l.id}" value="${d.x}" oninput="syncFromSidebar('${l.id}')"></div>
            <div><label>Y (px)</label><input type="number" id="y_${l.id}" value="${d.y}" oninput="syncFromSidebar('${l.id}')"></div>
            <div><label>L (px)</label><input type="number" id="w_${l.id}" value="${d.w}" oninput="syncFromSidebar('${l.id}')"></div>
            <div><label>A (px)</label><input type="number" id="h_${l.id}" value="${d.h}" oninput="syncFromSidebar('${l.id}')"></div>
        </div>` : `<p style="font-size:0.78rem;color:#64748b;margin:4px 8px;">Tela Cheia — ocupa 100% do canvas.</p>`}

        <div class="layer-controls" style="margin-top:6px;">
            ${l.hasChroma  ? `<label class="cb-wrap"><input type="checkbox" id="chroma_${l.id}" ${d.chroma ? 'checked' : ''}> Chroma Key</label>` : '<div></div>'}
            ${l.hasSortear ? `<label class="cb-wrap"><input type="checkbox" id="rand_${l.id}"   ${d.random ? 'checked' : ''}> Sortear Trecho</label>` : '<div></div>'}
            ${l.isExtra    ? `<button onclick="removeLayer('${l.id}')" class="btn-remove">✕ Remover</button>` : '<div></div>'}
        </div>
        
        ${l.id === 'lay_musica_onda' ? `
        <div class="layer-controls" style="margin-top:6px;">
            <label style="font-size:0.8rem; color:#fff;">Estilo da Onda:</label>
            <select id="wave_style_${l.id}" onchange="syncFromSidebar('${l.id}')" style="background:#1a1a2e; color:#fff; border:1px solid #475569; border-radius:4px; padding:2px; flex:1;">
                <option value="freqs" ${d.wave_style === 'freqs' ? 'selected' : ''}>EQ Trap (Barras)</option>
                <option value="vectorscope" ${d.wave_style === 'vectorscope' ? 'selected' : ''}>Vectorscope (Estrela/Trap Nation)</option>
                <option value="cqt" ${d.wave_style === 'cqt' ? 'selected' : ''}>CQT (Espectro Cromático)</option>
                <option value="osc" ${d.wave_style === 'osc' ? 'selected' : ''}>Osciloscópio (Linha)</option>
            </select>
        </div>
        ` : ''}
    `;
    sidebar.appendChild(card);

    document.getElementById(`vis_${l.id}`).addEventListener('change', () => {
        layersData[l.id].visible = document.getElementById(`vis_${l.id}`).checked;
        updateBox(l);
    });
}

// ── BOX NO CANVAS
function renderCanvasBox(l, canvas) {
    const box = document.createElement('div');
    box.id = `box_${l.id}`;
    box.className = 'layer-box';
    box.style.position     = 'absolute';
    box.style.zIndex       = l.zIndex;
    box.style.display      = 'flex';
    box.style.alignItems   = 'center';
    box.style.justifyContent = 'center';
    box.style.overflow     = 'hidden';
    box.style.userSelect   = 'none';

    if (l.isFixed) {
        box.style.background = l.color + '55';
        box.style.border     = `3px solid ${l.color}`;
    } else {
        box.style.background = l.color + '33';
        box.style.border     = `3px dashed ${l.color}`;
    }

    const label = document.createElement('div');
    label.className = 'box-label';
    label.innerText  = l.title;
    box.appendChild(label);

    // Thumbnail — existe em TODOS os layers (imagem ou frame de vídeo)
    const thumb = document.createElement('img');
    thumb.id = `thumb_${l.id}`;
    thumb.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:fill;opacity:0.65;display:none;pointer-events:none;';
    box.appendChild(thumb);

    if (!l.isFullscreen) {
        const hSE = makeHandle(l, 'se', l.color);
        box.appendChild(hSE);
        const hE = makeHandle(l, 'e', '#fff');
        box.appendChild(hE);
        const hS = makeHandle(l, 's', '#fff');
        box.appendChild(hS);
        makeDraggable(box, l);
    } else {
        box.style.pointerEvents = 'none';
    }

    canvas.appendChild(box);
}

function makeHandle(l, dir, color) {
    const h = document.createElement('div');
    h.className = `resize-handle handle-${dir}`;
    h.style.cssText = `
        position:absolute; background:${color}; border:2px solid ${l.color};
        border-radius:${dir === 'se' ? '50%' : '3px'}; z-index:10; cursor:${dir}-resize;
        ${dir === 'se' ? 'width:18px;height:18px;right:-4px;bottom:-4px;' : ''}
        ${dir === 'e'  ? 'width:10px;height:40%;top:30%;right:-4px;' : ''}
        ${dir === 's'  ? 'height:10px;width:40%;left:30%;bottom:-4px;' : ''}
    `;
    makeResizable(h, l, dir);
    return h;
}

// ── GLOBAL STATE PARA ACTIVE LAYER & NUDGE
let activeLayerId = null;

function setActiveLayer(id) {
    activeLayerId = id;
    document.querySelectorAll('.layer-card').forEach(c => c.style.background = '#1e293b');
    const card = document.getElementById(`card_${id}`);
    if (card) card.style.background = '#334155'; // Destaca na sidebar
}

// ── SNAP GUIDES
function showSnapGuide(type, pos) {
    let guide = document.getElementById(`snap_${type}`);
    if (!guide) {
        guide = document.createElement('div');
        guide.id = `snap_${type}`;
        guide.className = `snap-guide ${type}`;
        document.getElementById('render-canvas').appendChild(guide);
    }
    guide.style.display = 'block';
    if (type === 'vertical') guide.style.left = Number.isFinite(pos) ? pos + 'px' : pos;
    else guide.style.top = Number.isFinite(pos) ? pos + 'px' : pos;
}

function hideSnapGuides() {
    ['vertical', 'horizontal'].forEach(t => {
        const g = document.getElementById(`snap_${t}`);
        if (g) g.style.display = 'none';
    });
}

// ── DRAG COM MAGNÉTICO (SNAPPING)
function makeDraggable(box, l) {
    box.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('resize-handle')) return;
        e.preventDefault();
        setActiveLayer(l.id);

        const startX = e.clientX, startY = e.clientY;
        const initX = layersData[l.id].x, initY = layersData[l.id].y;
        const { W, H } = getBaseWH();

        const move = (ev) => {
            let nx = Math.round(initX + (ev.clientX - startX) / currentZoom);
            let ny = Math.round(initY + (ev.clientY - startY) / currentZoom);

            const w = layersData[l.id].w;
            const h = layersData[l.id].h;
            const snap = 15; // px de atração magnética

            hideSnapGuides();

            // Eixo X
            const cx = Math.round((W - w) / 2);
            if (Math.abs(nx - cx) < snap) { nx = cx; showSnapGuide('vertical', '50%'); }
            else if (Math.abs(nx) < snap) { nx = 0; showSnapGuide('vertical', '0'); }
            else if (Math.abs(nx + w - W) < snap) { nx = W - w; showSnapGuide('vertical', '100%'); }

            // Eixo Y
            const cy = Math.round((H - h) / 2);
            if (Math.abs(ny - cy) < snap) { ny = cy; showSnapGuide('horizontal', '50%'); }
            else if (Math.abs(ny) < snap) { ny = 0; showSnapGuide('horizontal', '0'); }
            else if (Math.abs(ny + h - H) < snap) { ny = H - h; showSnapGuide('horizontal', '100%'); }

            layersData[l.id].x = nx;
            layersData[l.id].y = ny;
            updateBox(l);
            syncSidebarInputs(l.id);
        };
        const up = () => { 
            hideSnapGuides();
            document.removeEventListener('mousemove', move); 
            document.removeEventListener('mouseup', up); 
        };
        document.addEventListener('mousemove', move);
        document.addEventListener('mouseup', up);
    });
}

// ── RESIZE INDEPENDENTE W/H
function makeResizable(handle, l, dir) {
    handle.addEventListener('mousedown', (e) => {
        e.preventDefault(); e.stopPropagation();
        const startX = e.clientX, startY = e.clientY;
        const initW = layersData[l.id].w, initH = layersData[l.id].h;

        const move = (ev) => {
            const dx = (ev.clientX - startX) / currentZoom;
            const dy = (ev.clientY - startY) / currentZoom;
            if (dir === 'se') {
                const d = Math.abs(dx) > Math.abs(dy) ? dx : dy;
                layersData[l.id].w = Math.max(50, Math.round(initW + d));
                layersData[l.id].h = Math.max(50, Math.round(initH + d * (initH / initW)));
            } else if (dir === 'e') {
                layersData[l.id].w = Math.max(50, Math.round(initW + dx));
            } else if (dir === 's') {
                layersData[l.id].h = Math.max(50, Math.round(initH + dy));
            }
            updateBox(l);
            syncSidebarInputs(l.id);
        };
        const up = () => { document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up); };
        document.addEventListener('mousemove', move);
        document.addEventListener('mouseup', up);
    });
}

// ── SYNC SIDEBAR → DATA
function syncFromSidebar(id) {
    const l = layersDefs.find(l => l.id === id);
    if (!l || l.isFullscreen) return;
    const xVal = parseInt(document.getElementById(`x_${id}`).value) || 0;
    const yVal = parseInt(document.getElementById(`y_${id}`).value) || 0;
    const wVal = parseInt(document.getElementById(`w_${id}`).value) || 100;
    const hVal = parseInt(document.getElementById(`h_${id}`).value) || 100;

    layersData[id].x = xVal;
    layersData[id].y = yVal;
    layersData[id].w = wVal;
    layersData[id].h = hVal;
    
    if (id === 'lay_musica_onda') {
        const styleSel = document.getElementById(`wave_style_${id}`);
        if (styleSel) layersData[id].wave_style = styleSel.value;
    }

    updateBox(l);
}

// ── SYNC DATA → SIDEBAR
function syncSidebarInputs(id) {
    const d = layersData[id];
    const xi = document.getElementById(`x_${id}`); if (xi) xi.value = d.x;
    const yi = document.getElementById(`y_${id}`); if (yi) yi.value = d.y;
    const wi = document.getElementById(`w_${id}`); if (wi) wi.value = d.w;
    const hi = document.getElementById(`h_${id}`); if (hi) hi.value = d.h;
}

// ── UPDATE BOX VISUAL
function updateBox(l) {
    const box = document.getElementById(`box_${l.id}`);
    if (!box) return;
    const d = layersData[l.id];

    if (!d.visible) { box.style.display = 'none'; return; }
    box.style.display = 'flex';

    if (l.isFullscreen) {
        box.style.cssText += ';width:100%;height:100%;left:0;top:0;';
    } else {
        box.style.width  = `${d.w}px`;
        box.style.height = `${d.h}px`;
        box.style.left   = `${d.x}px`;
        box.style.top    = `${d.y}px`;
    }
}

function updateAllBoxes() { layersDefs.forEach(l => updateBox(l)); }

function updateVisualOrder() {
    const sidebar = document.getElementById('layers-container');
    layersDefs.sort((a, b) => a.zIndex - b.zIndex);
    layersDefs.forEach(l => {
        const box = document.getElementById(`box_${l.id}`);
        if (box) box.style.zIndex = l.zIndex;
        const card = document.getElementById(`card_${l.id}`);
        if (card) sidebar.appendChild(card);
    });
}

function moveLayerUp(id) {
    const idx = layersDefs.findIndex(l => l.id === id);
    if (idx <= 0) return;
    // Só troca com camadas não-fullscreen adjacentes
    let target = idx - 1;
    while (target >= 0 && layersDefs[target].isFullscreen) target--;
    if (target < 0) return;
    [layersDefs[idx], layersDefs[target]] = [layersDefs[target], layersDefs[idx]];
    // Reordena zIndex
    layersDefs.forEach((l, i) => { l.zIndex = i; });
    updateVisualOrder();
}

function moveLayerDown(id) {
    const idx = layersDefs.findIndex(l => l.id === id);
    if (idx >= layersDefs.length - 1) return;
    let target = idx + 1;
    while (target < layersDefs.length && layersDefs[target].isFullscreen) target++;
    if (target >= layersDefs.length) return;
    [layersDefs[idx], layersDefs[target]] = [layersDefs[target], layersDefs[idx]];
    layersDefs.forEach((l, i) => { l.zIndex = i; });
    updateVisualOrder();
}

// ── THUMBNAIL: via API (FFmpeg) OU direto pelo File API
function onPathInput(id) {
    // Se o user digitou um caminho manualmente, limpa o thumb anterior
    const thumb = document.getElementById(`thumb_${id}`);
    if (thumb) { thumb.src = ''; thumb.style.display = 'none'; }
}

async function loadThumb(id) {
    const pathEl = document.getElementById(`path_${id}`);
    if (!pathEl) return;
    const path = pathEl.value.trim();
    if (!path) { 
        // Tenta usar a URL armazenada se existe (após browseFile)
        const stored = layersData[id]?._localUrl;
        if (stored) { applyThumb(id, stored); return; }
        alert('Selecione ou digite um arquivo primeiro.'); 
        return; 
    }

    const ext = path.split('.').pop().toLowerCase();
    const isImage = ['png','jpg','jpeg','webp','gif','bmp'].includes(ext);

    if (isImage) {
        // Para imagens locais: usa a API do servidor
        try {
            const r = await fetch(`/api/thumb?path=${encodeURIComponent(path)}`);
            if (r.ok) { applyThumb(id, URL.createObjectURL(await r.blob())); return; }
        } catch {}
    }
    // Para vídeos e fallback: usa a API de thumb
    try {
        const r = await fetch(`/api/thumb?path=${encodeURIComponent(path)}`);
        if (r.ok) { applyThumb(id, URL.createObjectURL(await r.blob())); }
        else       { alert('Não foi possível gerar preview. Verifique o caminho.'); }
    } catch(e) {
        alert('Servidor offline ou FFmpeg não disponível.');
    }
}

function applyThumb(id, url) {
    const img = document.getElementById(`thumb_${id}`);
    if (img) { 
        img.src = url; 
        img.style.display = 'block'; 
        
        img.onload = () => {
            const l = layersDefs.find(x => x.id === id);
            if (l && !l.isFullscreen) {
                const nw = img.naturalWidth;
                const nh = img.naturalHeight;
                if (nw > 0 && nh > 0) {
                    const d = layersData[id];
                    const aspect = nw / nh;
                    // Mantém a largura atual e corrige a altura para o formato nativo
                    d.h = Math.round(d.w / aspect);
                    syncSidebarInputs(id);
                    updateBox(l);
                }
            }
            img.onload = null;
        };
    }
    // Esconde o label de texto quando tem thumb
    const label = document.querySelector(`#box_${id} .box-label`);
    if (label) label.style.display = 'none';
}

// ── FILE BROWSER (abre via API do Python para retornar Caminho Absoluto)
async function browseFile(id) {
    try {
        // Obtém o botão via document para evitar dependência do objeto 'event' implícito
        const btn = document.querySelector(`#card_${id} .btn-mini[onclick*="browseFile"]`);
        const originalText = btn ? btn.innerHTML : '📁';
        if (btn) btn.innerHTML = '⌛';
        
        const res = await fetch('https://api.apolloedit.com/api/browse_file');
        const data = await res.json();
        
        btn.innerHTML = originalText;

        if (data.status === 'success' && data.path) {
            const pathEl = document.getElementById(`path_${id}`);
            if (pathEl) pathEl.value = data.path;
            layersData[id].path = data.path;
            
            // Agora que temos o path absoluto, podemos carregar usando FFmpeg!
            loadThumb(id);
        }
    } catch (e) {
        console.error("Erro ao buscar arquivo localmente:", e);
    }
}

// ── RENOMEAR CAMADA EXTRA
window.renameLayer = function(id, newTitle) {
    const l = layersDefs.find(x => x.id === id);
    if (l) {
        l.title = newTitle;
        // Atualiza o box-label no canvas
        const label = document.querySelector(`#box_${id} .box-label`);
        if (label) label.innerText = newTitle;
    }
};

// ── ADICIONAR CAMADA EXTRA (sempre FIXA por padrão, livre de isFullscreen)
function addExtraLayer() {
    extraCount++;
    const id = `lay_extra_${extraCount}`;
    const { W, H } = getBaseWH();
    const l = {
        id, title: `Barra/Moldura ${extraCount}`,
        zIndex: 10 + extraCount, color: '#06b6d4',
        isFixed: true,   // ← Agora todas as extras são fixas por padrão (ex: barras, molduras)
        isFullscreen: false,
        hasChroma: true, hasSortear: true, isExtra: true,
        defaultW: Math.round(W * 0.4), defaultH: Math.round(H * 0.25),
        defaultX: 50, defaultY: 50
    };
    layersDefs.push(l);
    initLayerData(l);

    const sidebar = document.getElementById('layers-container');
    const canvas  = document.getElementById('render-canvas');
    renderSidebarCard(l, sidebar);
    renderCanvasBox(l, canvas);
    updateBox(l);
}

// ── ADICIONAR CAMADA MUSICAL (Onda Sonora, Título, Progresso)
function addMusicLayer(type) {
    // Verifica se já existe, se existir, apenas seleciona
    const existing = layersDefs.find(l => l.id === `lay_musica_${type}`);
    if (existing) {
        setActiveLayer(existing.id);
        alert(`A camada de ${type} já existe no template.`);
        return;
    }
    
    const id = `lay_musica_${type}`;
    const { W, H } = getBaseWH();
    
    let title = "🎵 Camada Musical";
    let color = "#eab308";
    let defaultW = 500, defaultH = 100;
    
    if (type === 'onda') {
        title = "🎵 Onda Sonora (Visualizer)";
        color = "#ec4899";
        defaultW = W;
        defaultH = Math.round(H * 0.15);
    } else if (type === 'titulo') {
        title = "🎵 Título da Música";
        color = "#eab308";
        defaultW = Math.round(W * 0.8);
        defaultH = Math.round(H * 0.1);
    } else if (type === 'progresso') {
        title = "🎵 Barra de Progresso";
        color = "#ef4444";
        defaultW = W;
        defaultH = 20;
    } else if (type === 'capa') {
        title = "🎵 Capa da Música";
        color = "#8b5cf6";
        defaultW = 400;
        defaultH = 400;
    }
    
    const l = {
        id, title,
        zIndex: 20, color,
        isFixed: false,   // Variável porque não precisa de arquivo
        isFullscreen: false,
        hasChroma: false, hasSortear: false, isExtra: true, isMusic: true,
        defaultW, defaultH,
        defaultX: Math.round((W - defaultW) / 2), defaultY: Math.round(H * 0.7)
    };
    layersDefs.push(l);
    initLayerData(l);

    const sidebar = document.getElementById('layers-container');
    const canvas  = document.getElementById('render-canvas');
    renderSidebarCard(l, sidebar);
    renderCanvasBox(l, canvas);
    updateBox(l);
    
    // Adicionar um CSS placeholder específico para diferenciar a caixa no canvas
    const box = document.getElementById(`box_${id}`);
    if (box) {
        if (type === 'onda') {
            box.style.background = `repeating-linear-gradient(90deg, transparent, transparent 5px, ${color} 5px, ${color} 10px)`;
            box.style.opacity = '0.5';
        } else if (type === 'titulo') {
            box.innerHTML += `<div style="font-size:2rem; font-weight:bold; color:white; text-shadow: 2px 2px 0 #000;">NOME DA MÚSICA</div>`;
        } else if (type === 'progresso') {
            box.style.background = `linear-gradient(90deg, ${color} 50%, transparent 50%)`;
            box.style.border = `2px solid ${color}`;
        } else if (type === 'capa') {
            box.style.background = `linear-gradient(135deg, ${color}33, ${color}88)`;
            box.innerHTML += `<div style="font-size:3rem;">🖼️</div>`;
        }
    }
}

function removeLayer(id) {
    layersDefs = layersDefs.filter(l => l.id !== id);
    delete layersData[id];
    document.getElementById(`card_${id}`)?.remove();
    document.getElementById(`box_${id}`)?.remove();
}




// ── CANVAS CONTROLS
function setupCanvasControls() {
    const canvas     = document.getElementById('render-canvas');
    const scaler     = document.getElementById('canvas-scaler');
    const wrapper    = document.querySelector('.canvas-wrapper');
    const zoomSlider = document.getElementById('workspace-zoom');
    const zoomVal    = document.getElementById('zoom-val');

    // ─── ZOOM: a sacada é setar width/height REAL no scaler para criar scroll no DOM ───
    const updateZoom = (val) => {
        currentZoom = val / 100;
        zoomVal.innerText = `${Math.round(val)}%`;
        zoomSlider.value = val;
        
        const { W, H } = getBaseWH();
        
        // 1) O canvas fica no tamanho nativo e usa transform para aparecer em escala
        canvas.style.transformOrigin = 'top left';
        canvas.style.transform = `scale(${currentZoom})`;
        canvas.style.margin = '0';
        
        // 2) O scaler OCUPA o espaço real escalado no DOM → cria barras de scroll reais
        scaler.style.width  = `${W * currentZoom}px`;
        scaler.style.height = `${H * currentZoom}px`;
    };

    zoomSlider.addEventListener('input', (e) => updateZoom(e.target.value));

    const fitToScreen = () => {
        const { W, H } = getBaseWH();
        const availableW = wrapper.clientWidth  - 100;
        const availableH = wrapper.clientHeight - 100;
        
        const scaleW = availableW / W;
        const scaleH = availableH / H;
        
        let bestScale = Math.min(scaleW, scaleH) * 100;
        if (bestScale > 150) bestScale = 150;
        if (bestScale < 5)   bestScale = 5;
        
        updateZoom(bestScale);
    };

    document.getElementById('btn-fit').addEventListener('click', fitToScreen);
    setTimeout(fitToScreen, 150);

    document.getElementsByName('canvas_format').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentFormat = e.target.value;
            const { W, H } = getBaseWH();
            canvas.className = `canvas ${currentFormat}`;
            canvas.querySelector('.canvas-guide').innerText = `Tela: ${W}x${H}`;
            fitToScreen();
            updateAllBoxes();
        });
    });

    // ─── PAN (Mãozinha): Espaço+Drag OU Botão do Meio ───────────────────────────────
    let isPanning    = false;
    let isSpaceDown  = false;
    let panStartX    = 0;
    let panStartY    = 0;
    let panScrollLeft = 0;
    let panScrollTop  = 0;

    window.addEventListener('keydown', (e) => {
        // Ignora atalhos se o foco estiver num input (salvo o checkbox)
        if (document.activeElement.tagName === 'INPUT' && document.activeElement.type !== 'checkbox') return;
        if (document.activeElement.tagName === 'TEXTAREA') return;

        if (e.code === 'Space') {
            e.preventDefault();
            isSpaceDown = true;
            wrapper.style.cursor = 'grab';
        }

        // ── AJUSTE FINO (NUDGE) COM SETINHAS
        if (activeLayerId && ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
            const l = layersDefs.find(x => x.id === activeLayerId);
            const d = layersData[activeLayerId];
            if (l && !l.isFullscreen && !d.locked) {
                e.preventDefault();
                const step = e.shiftKey ? 10 : 1; // Shift acelera o pulo
                if (e.code === 'ArrowUp') d.y -= step;
                if (e.code === 'ArrowDown') d.y += step;
                if (e.code === 'ArrowLeft') d.x -= step;
                if (e.code === 'ArrowRight') d.x += step;
                updateBox(l);
                syncSidebarInputs(activeLayerId);
            }
        }
    });

    window.addEventListener('keyup', (e) => {
        if (e.code === 'Space') {
            isSpaceDown = false;
            if (!isPanning) wrapper.style.cursor = 'default';
        }
    });

    wrapper.addEventListener('mousedown', (e) => {
        if (isSpaceDown || e.button === 1) {
            e.preventDefault();
            isPanning = true;
            wrapper.style.cursor = 'grabbing';
            panStartX    = e.clientX;
            panStartY    = e.clientY;
            panScrollLeft = wrapper.scrollLeft;
            panScrollTop  = wrapper.scrollTop;
        }
    });

    window.addEventListener('mousemove', (e) => {
        if (!isPanning) return;
        e.preventDefault();
        const dx = e.clientX - panStartX;
        const dy = e.clientY - panStartY;
        wrapper.scrollLeft = panScrollLeft - dx;
        wrapper.scrollTop  = panScrollTop  - dy;
    });

    window.addEventListener('mouseup', () => {
        if (isPanning) {
            isPanning = false;
            wrapper.style.cursor = isSpaceDown ? 'grab' : 'default';
        }
    });

    // ─── ZOOM com scroll do mouse (Ctrl+Wheel) ────────────────────────────────────
    wrapper.addEventListener('wheel', (e) => {
        if (e.ctrlKey) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -5 : 5;
            const newVal = Math.max(5, Math.min(150, currentZoom * 100 + delta));
            updateZoom(newVal);
        }
    }, { passive: false });
}





function setupToolbar() {
    document.getElementById('btn-save').addEventListener('click', saveProfile);
    document.getElementById('btn-load').addEventListener('click', loadProfile);
    document.getElementById('btn-add-layer').addEventListener('click', addExtraLayer);
    
    // Botões Musicais
    const btnWave = document.getElementById('btn-add-wave');
    const btnTitle = document.getElementById('btn-add-title');
    const btnProg = document.getElementById('btn-add-prog');
    const btnCapa = document.getElementById('btn-add-capa');
    if (btnWave) btnWave.addEventListener('click', () => addMusicLayer('onda'));
    if (btnTitle) btnTitle.addEventListener('click', () => addMusicLayer('titulo'));
    if (btnProg) btnProg.addEventListener('click', () => addMusicLayer('progresso'));
    if (btnCapa) btnCapa.addEventListener('click', () => addMusicLayer('capa'));
}

// ── GATHER PROFILE DATA
function gatherProfileData() {
    const name   = document.getElementById('profile-name').value || 'perfil_padrao';
    const format = document.querySelector('input[name="canvas_format"]:checked').value;
    const data   = { profile_name: name, format, layers: {} };

    layersDefs.forEach(l => {
        const d = layersData[l.id];
        const entry = {
            visible: document.getElementById(`vis_${l.id}`)?.checked ?? true,
            x:  l.isFullscreen ? 0 : d.x,
            y:  l.isFullscreen ? 0 : d.y,
            w:  l.isFullscreen ? null : d.w,
            h:  l.isFullscreen ? null : d.h,
            // compatibilidade legada com "scale"
            scale: l.isFullscreen ? 100 : Math.round((d.w / (format === 'horizontal' ? 1920 : 1080)) * 100),
            chroma: l.hasChroma  ? (document.getElementById(`chroma_${l.id}`)?.checked ?? false) : false,
            random: l.hasSortear ? (document.getElementById(`rand_${l.id}`)?.checked  ?? false) : false,
            zIndex: l.zIndex,
            wave_style: d.wave_style
        };
        // Camadas FIXAS: também salvam o path
        if (l.isFixed && d.path) {
            entry.path = document.getElementById(`path_${l.id}`)?.value ?? '';
        }
        // Camadas VARIÁVEIS: path vazio (não salvo, pois muda a cada render)
        data.layers[l.id] = entry;
    });

    return data;
}

// ── SAVE
async function saveProfile() {
    const btn = document.getElementById('btn-save');
    btn.innerText = '🖼️ Gerando Preview...';
    const payload = gatherProfileData();

    // Captura screenshot do Canvas
    const renderCanvas = document.getElementById('render-canvas');
    let previewBase64 = '';
    try {
        const canvasShot = await html2canvas(renderCanvas, {
            backgroundColor: '#000000',
            scale: 0.5,
            ignoreElements: (el) => el.classList.contains('canvas-guide')
        });
        previewBase64 = canvasShot.toDataURL('image/jpeg', 0.7);
    } catch(err) {
        console.warn('html2canvas falhou — salvando sem preview:', err);
    }
    payload.preview_b64 = previewBase64;

    btn.innerText = 'Salvando...';
    try {
        const r = await fetch('https://api.apolloedit.com/api/save_profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await r.json();
        if (res.status === 'success') {
            btn.style.background = '#10b981';
            btn.innerText = '✅ Salvo!';
            loadProfileList();
        } else {
            alert('Erro: ' + res.message);
        }
    } catch(e) {
        alert('Servidor offline. Certifique-se que o Python está rodando.');
    } finally {
        // SEMPRE restaura o botão, mesmo se ocorrer erro
        setTimeout(() => { btn.style.background = ''; btn.innerText = '💾 Salvar no Apollo'; }, 2500);
    }
}

// ── LIST E PREVIEW
async function loadProfileList() {
    try {
        const r = await fetch('https://api.apolloedit.com/api/list_profiles');
        const res = await r.json();
        const sel = document.getElementById('profile-list');
        if (res.status === 'success') {
            sel.innerHTML = '<option value="">Selecione...</option>';
            res.profiles.forEach(p => sel.innerHTML += `<option value="${p}">${p}</option>`);
        }
    } catch(e) { /* offline */ }
}

// ── LISTENERS DE GESTÃO DE TEMPLATES
document.addEventListener('DOMContentLoaded', () => {
    const sel = document.getElementById('profile-list');
    const previewBox = document.getElementById('template-preview-box');
    const nameLabel = document.getElementById('selected-profile-name');
    const btnDelete = document.getElementById('btn-delete-profile');
    const btnRename = document.getElementById('btn-rename-profile');

    // Ao selecionar um perfil, exibe a imagem de preview
    if (sel) {
        sel.addEventListener('change', () => {
            const name = sel.value;
            if (nameLabel) nameLabel.innerText = name || 'Nenhum perfil selecionado';
            if (!name) {
                if (previewBox) previewBox.innerHTML = '<span style="color: #475569; font-size: 0.82rem;">Sem preview...<br><small>Selecione um perfil acima</small></span>';
                return;
            }
            // Carrega preview (imagem PNG salva junto com o template)
            if (previewBox) {
                const url = `/api/preview_image?name=${encodeURIComponent(name)}&t=${Date.now()}`;
                previewBox.innerHTML = `<img src="${url}" style="max-width: 100%; max-height: 100%; object-fit: contain;" onerror="this.parentElement.innerHTML='<span style=\\'color:#64748b;font-size:0.8rem;text-align:center;padding:10px;display:block;\\'>📷 Sem screenshot salvo</span>'">`;
            }
        });
    }

    // ── RENOMEAR PERFIL
    if (btnRename) {
        btnRename.addEventListener('click', async () => {
            const name = sel?.value;
            if (!name) { alert('Selecione um perfil primeiro!'); return; }
            const newName = prompt(`Novo nome para o perfil "${name}":`, name);
            if (!newName || newName === name) return;
            try {
                const r = await fetch('https://api.apolloedit.com/api/rename_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ old_name: name, new_name: newName })
                });
                const data = await r.json();
                if (data.status === 'success') {
                    alert(`Perfil renomeado para "${newName}"!`);
                    await loadProfileList();
                    // Seleciona o perfil renomeado na lista
                    const updated = document.getElementById('profile-list');
                    if (updated) {
                        updated.value = newName;
                        updated.dispatchEvent(new Event('change'));
                    }
                } else {
                    alert(`Erro: ${data.message}`);
                }
            } catch(e) {
                alert('Falha na conexão com o servidor Python.');
            }
        });
    }

    // ── DELETAR PERFIL
    if (btnDelete) {
        btnDelete.addEventListener('click', async () => {
            const name = sel?.value;
            if (!name) { alert('Selecione um perfil primeiro!'); return; }
            if (confirm(`Tem certeza que deseja EXCLUIR "${name}" permanentemente?`)) {
                try {
                    const r = await fetch(`/api/delete_profile?name=${encodeURIComponent(name)}`);
                    const data = await r.json();
                    if (data.status === 'success') {
                        if (previewBox) previewBox.innerHTML = '<span style="color: #475569; font-size: 0.82rem;">Sem preview...</span>';
                        if (nameLabel) nameLabel.innerText = 'Nenhum perfil selecionado';
                        await loadProfileList();
                    } else {
                        alert(`Erro ao excluir: ${data.message}`);
                    }
                } catch(e) {
                    alert('Falha na conexão com o servidor Python.');
                }
            }
        });
    }
});

// ── LOAD
async function loadProfile() {
    const name = document.getElementById('profile-list').value;
    if (!name) return;
    try {
        const r = await fetch(`/api/load_profile?name=${name}`);
        const res = await r.json();
        if (res.status !== 'success') { alert('Perfil não encontrado.'); return; }

        const data = res.data;
        document.getElementById('profile-name').value = data.profile_name || name;

        if (data.format) {
            currentFormat = data.format;
            document.querySelector(`input[name="canvas_format"][value="${data.format}"]`).checked = true;
            const canvas = document.getElementById('render-canvas');
            const { W, H } = getBaseWH();
            canvas.className = `canvas ${data.format}`;
            canvas.querySelector('.canvas-guide').innerText = `Tela: ${W}x${H}`;
        }

        if (data.layers) {
            Object.entries(data.layers).forEach(([id, ld]) => {
                let l = layersDefs.find(x => x.id === id);
                if (!l) {
                    // Trata camadas especiais de música se não existirem
                    if (id.startsWith('lay_musica_')) {
                        const type = id.replace('lay_musica_', '');
                        addMusicLayer(type);
                        l = layersDefs.find(x => x.id === id);
                        if (l && ld.zIndex !== undefined) l.zIndex = ld.zIndex;
                    } else {
                        // Camada extra não cadastrada: criar como FIXO
                        extraCount++;
                        l = { id, title: id, zIndex: ld.zIndex ?? (10 + extraCount), color: '#06b6d4', isFixed: true, isFullscreen: false, hasChroma: true, hasSortear: true, isExtra: true };
                        layersDefs.push(l);
                        initLayerData(l);
                    }
                } else if (ld.zIndex !== undefined) {
                    l.zIndex = ld.zIndex;
                }

                const { W, H } = getBaseWH();
                layersData[id].x = ld.x || 0;
                layersData[id].y = ld.y || 0;
                layersData[id].w = ld.w || (ld.scale ? Math.round((ld.scale / 100) * W) : W);
                layersData[id].h = ld.h || (ld.scale ? Math.round((ld.scale / 100) * H) : H);
                layersData[id].visible = ld.visible !== false;
                layersData[id].chroma  = ld.chroma || false;
                layersData[id].random  = ld.random  || false;
                if (ld.wave_style) layersData[id].wave_style = ld.wave_style;
                if (ld.path !== undefined) layersData[id].path = ld.path;

                // Sync the UI is handled by renderAll later
            });
            // Ordena o array pela zIndex restaurada e reconstrói a interface
            layersDefs.sort((a, b) => a.zIndex - b.zIndex);
            renderAll();
        }
    } catch(e) { alert('Erro ao carregar.'); }
}

window.onload = init;
