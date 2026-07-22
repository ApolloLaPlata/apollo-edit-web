/**
 * Apollo Bagagem Logic v2.0
 * Zona Temporária — Auto-tag + Timer de Expiração + Drag & Drop
 */

// ──────────────────────────────────────────
// ESTADO
// ──────────────────────────────────────────
const BagState = {
    files: [],          // [{id, name, size, type, uploadedAt, expiresAt, isSelected}]
    filter: 'all',
    searchQuery: '',
    selectedIds: new Set(),
    ctxTargetId: null,
};

// Mapa de extensão → tipo (igual ao da Garagem)
const TYPE_MAP = {
    photo:    ['jpg','jpeg','png','gif','webp','bmp','tiff','heic','avif','svg'],
    video:    ['mp4','mov','avi','mkv','webm','flv','wmv','m4v','3gp'],
    audio:    ['mp3','wav','ogg','flac','aac','m4a','opus','wma'],
    config:   ['json','yaml','yml','xml','toml','ini','cfg','conf','csv'],
    template: ['apollotemplate','zip'],
};
const TYPE_ICONS = { photo:'fa-image', video:'fa-film', audio:'fa-music', config:'fa-sliders-h', ia:'fa-wand-magic-sparkles', template:'fa-box-open' };
const TYPE_LABELS = { photo:'Foto', video:'Vídeo', audio:'Áudio', config:'Config', ia:'I.A.', template:'Template' };

function detectType(filename, isIA = false) {
    if (isIA) return 'ia';
    const ext = filename.split('.').pop().toLowerCase();
    for (const [type, exts] of Object.entries(TYPE_MAP)) {
        if (exts.includes(ext)) return type;
    }
    return 'config';
}

function makeExpiry(hoursFromNow = 24) {
    return new Date(Date.now() + hoursFromNow * 3600 * 1000);
}

// ──────────────────────────────────────────
// MOCK DATA
// ──────────────────────────────────────────
function loadMockBagagem() {
    const now = Date.now();
    BagState.files = [
        { id: 'b1', name: 'webcam_take1.mp4',          size: '145 MB', type: 'video',  uploadedAt: new Date(now - 3*3600000),  expiresAt: makeExpiry(21) },
        { id: 'b2', name: 'pack_baixado_temp.zip',     size: '350 MB', type: 'template', uploadedAt: new Date(now - 18*3600000), expiresAt: makeExpiry(6) },
        { id: 'b3', name: 'screenshot_config.png',     size: '2.1 MB', type: 'photo',  uploadedAt: new Date(now - 1*3600000),  expiresAt: makeExpiry(23) },
        { id: 'b4', name: 'config_tentativa_rvc.json', size: '8 KB',   type: 'config', uploadedAt: new Date(now - 22*3600000), expiresAt: makeExpiry(2) },
        { id: 'b5', name: 'IA_flux_banner_v2.jpg',     size: '4.2 MB', type: 'ia',     uploadedAt: new Date(now - 30*60000),   expiresAt: makeExpiry(23.5) },
    ];
}

// ──────────────────────────────────────────
// TIMER GLOBAL — Regressivo
// ──────────────────────────────────────────
function formatTime(ms) {
    if (ms <= 0) return '00:00:00';
    const h = Math.floor(ms / 3600000);
    const m = Math.floor((ms % 3600000) / 60000);
    const s = Math.floor((ms % 60000) / 1000);
    return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}

function getExpiryLabel(expiresAt) {
    const ms = expiresAt - Date.now();
    if (ms <= 0) return { label: 'EXPIRADO', cls: 'critical' };
    if (ms < 3 * 3600000) return { label: formatTime(ms), cls: 'critical' };
    if (ms < 8 * 3600000) return { label: formatTime(ms), cls: 'warning' };
    return { label: formatTime(ms), cls: 'safe' };
}

function tickTimers() {
    // Atualiza chip de expiração em cada card
    BagState.files.forEach(f => {
        const chip = document.querySelector(`[data-file-id="${f.id}"] .expiry-chip`);
        if (chip) {
            const { label, cls } = getExpiryLabel(f.expiresAt);
            chip.textContent = label;
            chip.className = `expiry-chip ${cls}`;
        }
    });

    // Atualiza lista lateral de "Expirando em Breve"
    renderExpirySidebar();

    // Timer global (menor expiração)
    const soonest = BagState.files.reduce((min, f) => f.expiresAt < min ? f.expiresAt : min, Infinity);
    const timerEl = document.getElementById('global-timer');
    if (timerEl && isFinite(soonest)) {
        timerEl.textContent = formatTime(soonest - Date.now());
    }
}

function renderExpirySidebar() {
    const el = document.getElementById('expiry-sidebar-list');
    if (!el) return;
    const sorted = [...BagState.files].sort((a, b) => a.expiresAt - b.expiresAt).slice(0, 4);
    el.innerHTML = sorted.map(f => {
        const { label, cls } = getExpiryLabel(f.expiresAt);
        const shortName = f.name.length > 22 ? f.name.slice(0, 22) + '...' : f.name;
        return `<div class="expiry-item">
            <div class="expiry-item-name">${shortName}</div>
            <div class="expiry-item-timer ${cls}">⏱ ${label}</div>
        </div>`;
    }).join('');
}

// ──────────────────────────────────────────
// FILTROS
// ──────────────────────────────────────────
function bSetFilter(filter, el) {
    BagState.filter = filter;
    BagState.selectedIds.clear();
    document.querySelectorAll('.b-nav-item').forEach(n => n.classList.remove('active'));
    if (el) el.classList.add('active');
    renderGrid();
    updateStatus();
}

function bSearch(q) {
    BagState.searchQuery = q;
    renderGrid();
}

function getFilteredFiles() {
    let files = [...BagState.files];
    if (BagState.filter !== 'all') files = files.filter(f => f.type === BagState.filter);
    if (BagState.searchQuery.trim()) {
        const q = BagState.searchQuery.toLowerCase();
        files = files.filter(f => f.name.toLowerCase().includes(q));
    }
    return files.sort((a, b) => a.expiresAt - b.expiresAt); // mais urgentes primeiro
}

// ──────────────────────────────────────────
// RENDER
// ──────────────────────────────────────────
function renderGrid() {
    const grid = document.getElementById('b-file-grid');
    const files = getFilteredFiles();

    document.getElementById('b-status-count').textContent = `${files.length} item${files.length !== 1 ? 's' : ''}`;

    // Atualiza contadores da sidebar
    const counts = { all: BagState.files.length };
    BagState.files.forEach(f => { counts[f.type] = (counts[f.type] || 0) + 1; });
    ['all','photo','video','audio','config','ia'].forEach(t => {
        const el = document.getElementById(`b-count-${t}`);
        if (el) el.textContent = counts[t] || 0;
    });

    if (files.length === 0) {
        grid.innerHTML = `<div class="empty-state"><i class="fas fa-suitcase-rolling"></i><h3>Bagagem Vazia</h3><p>Arraste arquivos para cá ou faça upload. Eles ficarão disponíveis por 24 horas.</p></div>`;
        return;
    }

    grid.innerHTML = '';
    files.forEach(file => {
        const icon = TYPE_ICONS[file.type] || 'fa-file';
        const label = TYPE_LABELS[file.type] || file.type;
        const { label: expiryLabel, cls: expiryCls } = getExpiryLabel(file.expiresAt);
        const isSelected = BagState.selectedIds.has(file.id);

        const card = document.createElement('div');
        card.className = `b-file-card type-${file.type}${isSelected ? ' selected' : ''}`;
        card.dataset.fileId = file.id;
        card.innerHTML = `
            <div class="b-file-icon"><i class="fas ${icon}"></i></div>
            <div class="b-file-name" title="${file.name}">${file.name}</div>
            <div class="b-file-size">${file.size}</div>
            <div class="expiry-chip ${expiryCls}">${expiryLabel}</div>
        `;

        card.addEventListener('click', (e) => {
            if (!e.ctrlKey && !e.metaKey) BagState.selectedIds.clear();
            BagState.selectedIds.has(file.id) ? BagState.selectedIds.delete(file.id) : BagState.selectedIds.add(file.id);
            updateStatus();
            document.querySelectorAll('.b-file-card').forEach(c => {
                c.classList.toggle('selected', BagState.selectedIds.has(c.dataset.fileId));
            });
        });

        card.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            BagState.ctxTargetId = file.id;
            if (!BagState.selectedIds.has(file.id)) {
                BagState.selectedIds.clear();
                BagState.selectedIds.add(file.id);
                updateStatus();
                document.querySelectorAll('.b-file-card').forEach(c => {
                    c.classList.toggle('selected', BagState.selectedIds.has(c.dataset.fileId));
                });
            }
            showCtx(e.clientX, e.clientY);
        });

        // Duplo-clique: manda direto para a Garagem
        card.addEventListener('dblclick', () => {
            BagState.selectedIds.add(file.id);
            sendSelectedToGarage();
        });

        grid.appendChild(card);
    });
}

function updateStatus() {
    const n = BagState.selectedIds.size;
    document.getElementById('b-status-selected').textContent =
        n === 0 ? 'Nenhum item selecionado' : `${n} item${n !== 1 ? 's' : ''} selecionado${n !== 1 ? 's' : ''}`;
}

// ──────────────────────────────────────────
// UPLOAD (Drag & Drop + Input)
// ──────────────────────────────────────────
function handleUpload(event) {
    const fileList = event.target.files;
    Array.from(fileList).forEach(f => addFileToState(f));
    event.target.value = ''; // reset input
}

function addFileToState(browserFile) {
    const id = `b_${Date.now()}_${Math.random().toString(36).slice(2,7)}`;
    const sizeStr = formatBytes(browserFile.size);
    const type = detectType(browserFile.name);
    BagState.files.push({
        id, name: browserFile.name,
        size: sizeStr, type,
        uploadedAt: new Date(),
        expiresAt: makeExpiry(24),
    });
    renderGrid();
    showToast(`✅ "${browserFile.name}" adicionado à Bagagem!`);
}

function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes/1024).toFixed(1)} KB`;
    if (bytes < 1024**3) return `${(bytes/1024/1024).toFixed(1)} MB`;
    return `${(bytes/1024**3).toFixed(2)} GB`;
}

function onDragOver(e) { e.preventDefault(); document.getElementById('drop-zone').classList.add('drag-over'); }
function onDragLeave(e) { document.getElementById('drop-zone').classList.remove('drag-over'); }
function onDrop(e) {
    e.preventDefault();
    document.getElementById('drop-zone').classList.remove('drag-over');
    Array.from(e.dataTransfer.files).forEach(f => addFileToState(f));
}

// ──────────────────────────────────────────
// AÇÕES: MOVER PARA GARAGEM
// ──────────────────────────────────────────
function sendSelectedToGarage() {
    if (BagState.selectedIds.size === 0) { showToast('Selecione arquivos primeiro.'); return; }
    const moved = BagState.selectedIds.size;
    BagState.files = BagState.files.filter(f => !BagState.selectedIds.has(f.id));
    BagState.selectedIds.clear();
    renderGrid(); updateStatus();
    showToast(`🚘 ${moved} arquivo${moved !== 1 ? 's' : ''} movido${moved !== 1 ? 's' : ''} para a Garagem HD!`);
}

function sendAllToGarage() {
    const total = BagState.files.length;
    if (total === 0) { showToast('Bagagem vazia.'); return; }
    BagState.files = [];
    BagState.selectedIds.clear();
    renderGrid(); updateStatus();
    showToast(`🚘 ${total} arquivo${total !== 1 ? 's' : ''} salvo${total !== 1 ? 's' : ''} na Garagem HD!`);
}

function bDeleteSelected() {
    if (BagState.selectedIds.size === 0) { showToast('Selecione arquivos primeiro.'); return; }
    if (!confirm(`Excluir ${BagState.selectedIds.size} item(ns) permanentemente?`)) return;
    BagState.files = BagState.files.filter(f => !BagState.selectedIds.has(f.id));
    BagState.selectedIds.clear();
    renderGrid(); updateStatus();
    showToast('🗑️ Arquivos excluídos.');
}

// ──────────────────────────────────────────
// CONTEXT MENU
// ──────────────────────────────────────────
function showCtx(x, y) {
    const m = document.getElementById('b-ctx-menu');
    m.style.left = `${Math.min(x, window.innerWidth - 200)}px`;
    m.style.top  = `${Math.min(y, window.innerHeight - 150)}px`;
    m.classList.add('visible');
}
function hideCtx() { document.getElementById('b-ctx-menu').classList.remove('visible'); }

function bCtxSaveGarage() { sendSelectedToGarage(); hideCtx(); }
function bCtxEditor()      { showToast('🎬 Enviado ao Editor!'); hideCtx(); }
function bCtxDownload()    { showToast('⬇️ Download iniciado!'); hideCtx(); }
function bCtxDelete()      { bDeleteSelected(); hideCtx(); }

// ──────────────────────────────────────────
// TOAST
// ──────────────────────────────────────────
function showToast(msg) {
    let t = document.getElementById('bagagem-toast');
    if (!t) {
        t = document.createElement('div');
        t.id = 'bagagem-toast';
        t.style.cssText = 'position:fixed;bottom:50px;left:50%;transform:translateX(-50%);background:rgba(9,8,15,0.95);border:1px solid rgba(96,165,250,0.3);color:#e2e8f0;padding:10px 18px;border-radius:10px;font-size:13px;z-index:9999;transition:opacity 0.3s;pointer-events:none;backdrop-filter:blur(10px);';
        document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = '1';
    clearTimeout(t._to);
    t._to = setTimeout(() => { t.style.opacity = '0'; }, 3500);
}

// ──────────────────────────────────────────
// BOOT
// ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('b-file-grid')) return;
    loadMockBagagem();
    renderGrid();
    renderExpirySidebar();

    // Tick a cada segundo para atualizar timers
    setInterval(tickTimers, 1000);

    // Fecha ctx menu ao clicar fora
    document.addEventListener('click', hideCtx);
});
