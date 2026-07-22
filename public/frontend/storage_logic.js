/**
 * Apollo Garagem HD — Storage Logic v2.0
 * Sistema Híbrido: Auto-Tags + Álbuns Manuais + Filtros Inteligentes
 *
 * Arquitetura:
 * - Armazenamento é FLAT (todos os arquivos num único array).
 * - Cada arquivo recebe AUTO-TAGS na entrada (photo, video, audio, config, ia, template).
 * - Os "filtros" da sidebar são consultas sobre essas tags — não movem nenhum arquivo.
 * - Álbuns manuais guardam apenas REFERÊNCIAS (IDs) dos arquivos — sem duplicação.
 */

// ─────────────────────────────────────────────────────
// 1. ESTADO GLOBAL
// ─────────────────────────────────────────────────────
const GaragemState = {
    allFiles: [],          // Array plano (fonte da verdade)
    albums: [],            // Álbuns manuais [{id, name, fileIds[]}]
    activeFilter: 'all',   // 'all' | 'photo' | 'video' | 'audio' | 'config' | 'ia'
    activeAlbum: null,     // id do álbum ativo (null = sem álbum)
    searchQuery: '',
    viewMode: 'grid',      // 'grid' | 'list'
    selectedIds: new Set(),
    ctxTargetId: null,     // ID do arquivo do menu de contexto
};

// ─────────────────────────────────────────────────────
// 2. AUTO-TAGGER
// Detecta o tipo baseado na extensão do arquivo
// ─────────────────────────────────────────────────────
const TYPE_MAP = {
    // Fotos
    photo: ['jpg','jpeg','png','gif','webp','bmp','tiff','svg','ico','heic','avif'],
    // Vídeos
    video: ['mp4','mov','avi','mkv','webm','flv','wmv','m4v','3gp'],
    // Áudios
    audio: ['mp3','wav','ogg','flac','aac','m4a','opus','wma'],
    // Configurações/Dados
    config: ['json','yaml','yml','xml','toml','ini','cfg','conf','csv'],
    // Templates (monolíticos Apollo)
    template: ['apollotemplate','apollotmpl','zip'],
};

function autoTag(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    for (const [type, exts] of Object.entries(TYPE_MAP)) {
        if (exts.includes(ext)) return type;
    }
    return 'config'; // fallback
}

function autoTagBatch(filename, isIAGenerated = false) {
    if (isIAGenerated) return 'ia';
    return autoTag(filename);
}

// ─────────────────────────────────────────────────────
// 3. DADOS MOCK (substituir por chamadas Supabase)
// ─────────────────────────────────────────────────────
function loadMockData() {
    const raw = [
        { id: '1', name: 'hero_banner_final.jpg',             size: '2.4 MB',  isCustom: false, iaGenerated: false, createdAt: '2026-06-01' },
        { id: '2', name: 'logo_canal_dark_v3.png',            size: '450 KB',  isCustom: true,  iaGenerated: false, createdAt: '2026-06-02' },
        { id: '3', name: 'intro_dramatica_4k.mp4',            size: '850 MB',  isCustom: true,  iaGenerated: false, createdAt: '2026-06-03' },
        { id: '4', name: 'swoosh_epic_cinematic.mp3',          size: '3.2 MB',  isCustom: false, iaGenerated: false, createdAt: '2026-06-03' },
        { id: '5', name: 'config_shorts_basico.json',          size: '12 KB',   isCustom: false, iaGenerated: false, createdAt: '2026-06-04' },
        { id: '6', name: 'config_transicao_3d_custom.json',   size: '28 KB',   isCustom: true,  iaGenerated: false, createdAt: '2026-06-04' },
        { id: '7', name: 'IA_flux_carro_neon_0412.png',       size: '3.8 MB',  isCustom: false, iaGenerated: true,  createdAt: '2026-06-05' },
        { id: '8', name: 'IA_ltx_piloto_vitoria.mp4',         size: '45 MB',   isCustom: false, iaGenerated: true,  createdAt: '2026-06-06' },
        { id: '9', name: 'template_canal_dark_completo.apollotemplate', size: '1.2 GB', isCustom: true, iaGenerated: false, createdAt: '2026-06-06' },
        { id: '10', name: 'background_music_lofi.mp3',        size: '8.1 MB',  isCustom: false, iaGenerated: false, createdAt: '2026-06-07' },
        { id: '11', name: 'cena_amanecer_wide.jpg',           size: '5.1 MB',  isCustom: false, iaGenerated: false, createdAt: '2026-06-07' },
        { id: '12', name: 'config_voz_rvc_custom.yaml',       size: '4 KB',    isCustom: true,  iaGenerated: false, createdAt: '2026-06-08' },
    ];

    // AUTO-TAG na carga
    GaragemState.allFiles = raw.map(f => ({
        ...f,
        type: autoTagBatch(f.name, f.iaGenerated),
    }));

    // Álbuns iniciais de exemplo
    GaragemState.albums = [
        { id: 'a1', name: 'Projeto Carro 2024', fileIds: ['1', '3', '7'] },
        { id: 'a2', name: 'Recursos de Shorts', fileIds: ['4', '5', '10'] },
    ];
}

// ─────────────────────────────────────────────────────
// 4. MOTOR DE FILTRO (não move arquivos — apenas filtra)
// ─────────────────────────────────────────────────────
function getFilteredFiles() {
    let files = [...GaragemState.allFiles];

    // Filtro de álbum manual
    if (GaragemState.activeAlbum) {
        const album = GaragemState.albums.find(a => a.id === GaragemState.activeAlbum);
        if (album) files = files.filter(f => album.fileIds.includes(f.id));
    }

    // Filtro por tipo (smart tag)
    if (GaragemState.activeFilter !== 'all') {
        files = files.filter(f => f.type === GaragemState.activeFilter);
    }

    // Busca por nome
    if (GaragemState.searchQuery.trim()) {
        const q = GaragemState.searchQuery.toLowerCase();
        files = files.filter(f => f.name.toLowerCase().includes(q));
    }

    return files;
}

// ─────────────────────────────────────────────────────
// 5. AÇÕES DO USUÁRIO (filtros + álbuns)
// ─────────────────────────────────────────────────────
function setFilter(filter, chipEl) {
    GaragemState.activeFilter = filter;
    GaragemState.activeAlbum = null;
    GaragemState.selectedIds.clear();

    // Atualiza chips ativos
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    if (chipEl) chipEl.classList.add('active');

    // Desativa álbuns
    document.querySelectorAll('.album-item').forEach(a => a.classList.remove('active'));

    // Atualiza breadcrumb e barra de filtro ativo
    const labels = { all: 'Tudo', photo: '📷 Fotos', video: '🎬 Vídeos', audio: '🎵 Áudios', config: '⚙️ Configurações', ia: '✨ Gerações I.A.' };
    document.getElementById('bc-current').textContent = labels[filter] || filter;

    const filterBar = document.getElementById('active-filter-bar');
    if (filter === 'all') {
        filterBar.classList.add('hidden');
    } else {
        filterBar.classList.remove('hidden');
        document.getElementById('filter-pill-text').textContent = labels[filter];
    }

    renderGrid();
}

function setAlbum(albumId) {
    GaragemState.activeAlbum = albumId;
    GaragemState.activeFilter = 'all';
    GaragemState.selectedIds.clear();

    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.album-item').forEach(a => {
        a.classList.toggle('active', a.dataset.albumId === albumId);
    });

    const album = GaragemState.albums.find(a => a.id === albumId);
    document.getElementById('bc-current').textContent = `📁 ${album?.name || albumId}`;
    document.getElementById('active-filter-bar').classList.add('hidden');

    renderGrid();
}

function createAlbum() {
    const name = prompt('Nome do novo Álbum:');
    if (!name?.trim()) return;
    const album = { id: `a_${Date.now()}`, name: name.trim(), fileIds: [] };
    GaragemState.albums.push(album);
    renderAlbumList();
    showToast(`📁 Álbum "${name}" criado!`);
}

function searchFiles(q) {
    GaragemState.searchQuery = q;
    renderGrid();
}

function setView(mode) {
    GaragemState.viewMode = mode;
    document.getElementById('view-grid-btn').classList.toggle('active', mode === 'grid');
    document.getElementById('view-list-btn').classList.toggle('active', mode === 'list');
    renderGrid();
}

// ─────────────────────────────────────────────────────
// 6. RENDERIZAÇÃO
// ─────────────────────────────────────────────────────
const TYPE_ICONS = {
    photo:    'fa-image',
    video:    'fa-film',
    audio:    'fa-music',
    config:   'fa-sliders-h',
    ia:       'fa-wand-magic-sparkles',
    template: 'fa-box-open',
};
const TYPE_LABELS = {
    photo: 'Foto', video: 'Vídeo', audio: 'Áudio',
    config: 'Config', ia: 'I.A.', template: 'Template',
};

function renderGrid() {
    const grid = document.getElementById('file-grid');
    const files = getFilteredFiles();

    grid.className = `file-grid${GaragemState.viewMode === 'list' ? ' list-view' : ''}`;

    // Atualiza contagem no status bar
    document.getElementById('status-count').textContent = `${files.length} item${files.length !== 1 ? 's' : ''}`;
    document.getElementById('filter-result-count').textContent = `${files.length} arquivo${files.length !== 1 ? 's' : ''}`;

    if (files.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-box-open"></i>
                <h3>Nenhum arquivo aqui</h3>
                <p>${GaragemState.searchQuery ? 'Nenhum resultado para "' + GaragemState.searchQuery + '".' : 'Mova arquivos da Bagagem ou gere mídias com o Apollo Flow.'}</p>
            </div>`;
        return;
    }

    grid.innerHTML = '';
    files.forEach(file => {
        const isSelected = GaragemState.selectedIds.has(file.id);
        const icon = TYPE_ICONS[file.type] || 'fa-file';
        const label = TYPE_LABELS[file.type] || file.type;

        let badgeHTML = '';
        if (file.iaGenerated) {
            badgeHTML = `<span class="auto-tag ia">I.A.</span>`;
        } else if (file.isCustom) {
            badgeHTML = `<span class="auto-tag custom">CUSTOM</span>`;
        } else {
            badgeHTML = `<span class="auto-tag oficial">OFICIAL</span>`;
        }

        const card = document.createElement('div');
        card.className = `file-card type-${file.type}${isSelected ? ' selected' : ''}`;
        card.dataset.fileId = file.id;

        if (GaragemState.viewMode === 'list') {
            card.innerHTML = `
                ${badgeHTML}
                <div class="file-icon-wrap"><i class="fas ${icon}"></i></div>
                <div class="file-meta">
                    <div class="file-name" title="${file.name}">${file.name}</div>
                    <div class="file-tags-row">
                        <span class="type-pill">${label}</span>
                        <span class="file-size">${file.size}</span>
                        <span class="file-size" style="margin-left:auto;">${file.createdAt}</span>
                    </div>
                </div>`;
        } else {
            card.innerHTML = `
                ${badgeHTML}
                <div class="file-icon-wrap"><i class="fas ${icon}"></i></div>
                <div class="file-name" title="${file.name}">${file.name}</div>
                <span class="type-pill">${label}</span>
                <div class="file-size">${file.size}</div>`;
        }

        // Click: seleção (multi com Ctrl)
        card.addEventListener('click', (e) => {
            if (!e.ctrlKey && !e.metaKey) GaragemState.selectedIds.clear();
            if (GaragemState.selectedIds.has(file.id)) {
                GaragemState.selectedIds.delete(file.id);
            } else {
                GaragemState.selectedIds.add(file.id);
            }
            updateSelectionStatus();
            document.querySelectorAll('.file-card').forEach(c => {
                c.classList.toggle('selected', GaragemState.selectedIds.has(c.dataset.fileId));
            });
        });

        // Context menu
        card.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            GaragemState.ctxTargetId = file.id;
            if (!GaragemState.selectedIds.has(file.id)) {
                GaragemState.selectedIds.clear();
                GaragemState.selectedIds.add(file.id);
                updateSelectionStatus();
                document.querySelectorAll('.file-card').forEach(c => {
                    c.classList.toggle('selected', GaragemState.selectedIds.has(c.dataset.fileId));
                });
            }
            showCtxMenu(e.clientX, e.clientY);
        });

        grid.appendChild(card);
    });
}

function renderAlbumList() {
    const list = document.getElementById('album-list');
    list.innerHTML = GaragemState.albums.map(album => `
        <div class="album-item${GaragemState.activeAlbum === album.id ? ' active' : ''}" 
             data-album-id="${album.id}"
             onclick="setAlbum('${album.id}')"
             oncontextmenu="albumCtx(event, '${album.id}')">
            <i class="fas fa-folder"></i>
            <span class="album-name">${album.name}</span>
            <span class="album-count">${album.fileIds.length}</span>
        </div>
    `).join('');
}

function updateCounts() {
    const counts = { all: GaragemState.allFiles.length, photo: 0, video: 0, audio: 0, config: 0, ia: 0 };
    GaragemState.allFiles.forEach(f => { if (counts[f.type] !== undefined) counts[f.type]++; });
    Object.entries(counts).forEach(([type, count]) => {
        const el = document.getElementById(`count-${type}`);
        if (el) el.textContent = count;
    });
}

function updateSelectionStatus() {
    const n = GaragemState.selectedIds.size;
    document.getElementById('status-selected').textContent =
        n === 0 ? 'Nenhum item selecionado' : `${n} item${n !== 1 ? 's' : ''} selecionado${n !== 1 ? 's' : ''}`;
}

// ─────────────────────────────────────────────────────
// 7. CONTEXT MENU
// ─────────────────────────────────────────────────────
function showCtxMenu(x, y) {
    const menu = document.getElementById('ctx-menu');
    menu.style.left = `${Math.min(x, window.innerWidth - 200)}px`;
    menu.style.top  = `${Math.min(y, window.innerHeight - 200)}px`;
    menu.classList.add('visible');
}

function hideCtxMenu() { document.getElementById('ctx-menu').classList.remove('visible'); }

function ctxOpen() { showToast('📂 Abrindo arquivo...'); hideCtxMenu(); }
function ctxSendEditor() { showToast('🎬 Enviado para o Editor!'); hideCtxMenu(); }
function ctxDownload() { showToast('⬇️ Download iniciado!'); hideCtxMenu(); }
function ctxRename() {
    const file = GaragemState.allFiles.find(f => f.id === GaragemState.ctxTargetId);
    const newName = prompt('Renomear para:', file?.name || '');
    if (newName?.trim() && file) {
        file.name = newName.trim();
        file.type = autoTagBatch(newName.trim(), file.iaGenerated);
        renderGrid();
        updateCounts();
        showToast(`✏️ Renomeado para "${newName}"`);
    }
    hideCtxMenu();
}

function ctxAddToAlbum() {
    if (GaragemState.albums.length === 0) { createAlbum(); hideCtxMenu(); return; }
    const names = GaragemState.albums.map((a, i) => `${i + 1}. ${a.name}`).join('\n');
    const idx = parseInt(prompt(`Adicionar ao álbum:\n${names}\n\nDigite o número:`)) - 1;
    if (idx >= 0 && idx < GaragemState.albums.length) {
        const album = GaragemState.albums[idx];
        GaragemState.selectedIds.forEach(id => {
            if (!album.fileIds.includes(id)) album.fileIds.push(id);
        });
        renderAlbumList();
        showToast(`📁 Adicionado ao álbum "${album.name}"!`);
    }
    hideCtxMenu();
}

function ctxDelete() {
    if (!confirm(`Excluir ${GaragemState.selectedIds.size} item(ns)? Esta ação não pode ser desfeita.`)) {
        hideCtxMenu(); return;
    }
    GaragemState.allFiles = GaragemState.allFiles.filter(f => !GaragemState.selectedIds.has(f.id));
    GaragemState.albums.forEach(a => { a.fileIds = a.fileIds.filter(id => !GaragemState.selectedIds.has(id)); });
    GaragemState.selectedIds.clear();
    renderGrid(); renderAlbumList(); updateCounts(); updateSelectionStatus();
    showToast('🗑️ Arquivos excluídos.');
    hideCtxMenu();
}

function albumCtx(e, albumId) {
    e.preventDefault();
    const action = prompt(`Álbum: "${GaragemState.albums.find(a => a.id === albumId)?.name}"\n\n1. Renomear\n2. Excluir\n\nDigite o número:`);
    if (action === '1') {
        const album = GaragemState.albums.find(a => a.id === albumId);
        const newName = prompt('Novo nome:', album?.name);
        if (newName?.trim()) { album.name = newName.trim(); renderAlbumList(); }
    } else if (action === '2') {
        if (confirm('Excluir este álbum? Os arquivos NÃO serão deletados.')) {
            GaragemState.albums = GaragemState.albums.filter(a => a.id !== albumId);
            if (GaragemState.activeAlbum === albumId) { GaragemState.activeAlbum = null; }
            renderAlbumList(); renderGrid(); updateCounts();
        }
    }
}

// ─────────────────────────────────────────────────────
// 8. AÇÕES DE TOOLBAR
// ─────────────────────────────────────────────────────
function deleteSelected() {
    if (GaragemState.selectedIds.size === 0) { showToast('Selecione arquivos primeiro.'); return; }
    ctxDelete();
}

function uploadFromBagagem() {
    // Futura integração: abre modal da Bagagem para mover arquivos
    showToast('💼 Abrindo Bagagem para transferência...');
}

// ─────────────────────────────────────────────────────
// 9. TOAST
// ─────────────────────────────────────────────────────
function showToast(msg) {
    let t = document.getElementById('garagem-toast');
    if (!t) {
        t = document.createElement('div');
        t.id = 'garagem-toast';
        t.style.cssText = 'position:fixed;bottom:50px;left:50%;transform:translateX(-50%);background:rgba(9,11,17,0.95);border:1px solid rgba(250,204,21,0.3);color:#e2e8f0;padding:10px 18px;border-radius:10px;font-size:13px;z-index:9999;transition:opacity 0.3s;pointer-events:none;backdrop-filter:blur(10px);';
        document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = '1';
    clearTimeout(t._to);
    t._to = setTimeout(() => { t.style.opacity = '0'; }, 3500);
}

// ─────────────────────────────────────────────────────
// 10. BOOT
// ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Só inicializa na página Garagem
    if (!document.getElementById('file-grid')) return;

    loadMockData();
    renderGrid();
    renderAlbumList();
    updateCounts();

    // Fechar ctx menu ao clicar fora
    document.addEventListener('click', hideCtxMenu);

    // Deselecionar ao clicar no fundo
    document.getElementById('file-grid').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            GaragemState.selectedIds.clear();
            document.querySelectorAll('.file-card').forEach(c => c.classList.remove('selected'));
            updateSelectionStatus();
        }
    });
});
