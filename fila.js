/**
 * fila.js — Lógica da Fila Autônoma (Batch Queue)
 * Apollo Studio Web UI
 */

// ── Estado local
let filaData = [];
let selectedIdx = null;
let pollingInterval = null;
let logPollingInterval = null;
let enviarTimeline = false;
let hotfolderAtivo = false;
let ultimoLogCount = 0;

// ── Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarPerfis();
    startPolling();
});

// ════════════════════════════════════════════════════
// POLLING — Atualiza estado da fila a cada 2s
// ════════════════════════════════════════════════════
function startPolling() {
    fetchStatus();
    fetchLog();
    pollingInterval = setInterval(fetchStatus, 2000);
    logPollingInterval = setInterval(fetchLog, 1500);
}

async function fetchStatus() {
    try {
        const r = await fetch('/api/fila/status');
        if (!r.ok) return;
        const d = await r.json();
        filaData = d.fila || [];
        atualizarUI(d);
    } catch(e) {
        // servidor offline — não quebra a UI
    }
}

async function fetchLog() {
    try {
        const r = await fetch(`/api/fila/log?n=80`);
        if (!r.ok) return;
        const d = await r.json();
        const linhas = d.log || [];
        if (linhas.length !== ultimoLogCount) {
            ultimoLogCount = linhas.length;
            renderLog(linhas);
        }
    } catch(e) {}
}

// ════════════════════════════════════════════════════
// RENDER DA UI
// ════════════════════════════════════════════════════
function atualizarUI(d) {
    // Status badge do header
    const dot = document.getElementById('dot-status');
    const txt = document.getElementById('txt-status');
    if (d.rodando) {
        dot.className = 'dot running';
        txt.textContent = 'Renderizando...';
    } else {
        dot.className = 'dot';
        txt.textContent = d.total > 0 ? 'Fila pronta' : 'Aguardando';
    }

    // Stats
    document.getElementById('stat-total').textContent = d.total || 0;
    document.getElementById('stat-pend').textContent  = d.pendentes || 0;
    document.getElementById('stat-ok').textContent    = d.concluidos || 0;
    document.getElementById('stat-err').textContent   = d.erros || 0;

    // Progress
    const prog = d.progresso || 0;
    document.getElementById('progress-fill').style.width = prog + '%';
    if (d.rodando) {
        document.getElementById('progress-label').textContent = `Processando... ${prog}%`;
    } else if (prog === 100 && d.total > 0) {
        document.getElementById('progress-label').textContent = '✅ Fila concluída!';
    } else {
        document.getElementById('progress-label').textContent = 'Aguardando início...';
    }
    document.getElementById('eta-label').textContent = d.eta || '';

    // Botões
    document.getElementById('btn-iniciar').disabled = d.rodando;
    document.getElementById('btn-parar').disabled   = !d.rodando;

    // Hotfolder
    hotfolderAtivo = d.hotfolder_ativo;
    const tgl = document.getElementById('toggle-hotfolder');
    if (hotfolderAtivo) { tgl.classList.add('on'); } else { tgl.classList.remove('on'); }

    // Tabela
    renderTabela(d.fila || []);
}

function statusClass(status) {
    if (!status) return 'pendente';
    const s = status.toLowerCase();
    if (s.includes('pendente'))   return 'pendente';
    if (s.includes('renderizando')) return 'renderizando';
    if (s.includes('conclu'))    return 'concluido';
    if (s.includes('erro'))      return 'erro';
    if (s.includes('cancelado')) return 'cancelado';
    return 'pendente';
}

function renderTabela(fila) {
    const empty  = document.getElementById('empty-state');
    const table  = document.getElementById('queue-table');
    const tbody  = document.getElementById('queue-tbody');

    if (!fila || fila.length === 0) {
        empty.style.display = 'flex';
        table.style.display = 'none';
        return;
    }

    empty.style.display = 'none';
    table.style.display = 'table';

    tbody.innerHTML = '';
    fila.forEach((proj, i) => {
        const tr = document.createElement('tr');
        if (i === selectedIdx) tr.classList.add('active-row');
        tr.onclick = () => { selectedIdx = i; renderTabela(fila); };

        const audioBasename = proj.audio ? proj.audio.split(/[\\/]/).pop() : '—';
        const cls = statusClass(proj.status);

        tr.innerHTML = `
            <td class="num">${i + 1}</td>
            <td>
                <div style="font-weight:600">${escHtml(proj.nome || '—')}</div>
                <div class="path-text" title="${escHtml(proj.saida || '')}">${escHtml(proj.saida || '—')}</div>
            </td>
            <td>
                <div class="path-text" title="${escHtml(proj.audio || '')}">${escHtml(audioBasename)}</div>
                ${proj.musica ? `<div class="path-text" title="${escHtml(proj.musica)}">🎶 ${proj.musica.split(/[\\/]/).pop()}</div>` : ''}
            </td>
            <td>${escHtml(proj.perfil || '—')}</td>
            <td><span class="badge ${cls}">${escHtml(proj.status || '⏳ Pendente')}</span></td>
            <td style="color:var(--muted);font-size:12px">${escHtml(proj.duracao || '—')}</td>
            <td>
                <div class="row-actions">
                    <button class="mini-btn" onclick="event.stopPropagation();moverItemDireto(${i},-1)" title="Subir">⬆</button>
                    <button class="mini-btn" onclick="event.stopPropagation();moverItemDireto(${i},1)"  title="Descer">⬇</button>
                    <button class="mini-btn del" onclick="event.stopPropagation();removerItem(${i})" title="Remover">🗑</button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderLog(linhas) {
    const body = document.getElementById('log-body');
    const wasAtBottom = body.scrollHeight - body.scrollTop <= body.clientHeight + 20;

    body.innerHTML = linhas.map(l => {
        let cls = '';
        const ll = l.toLowerCase();
        if (ll.includes('erro') || ll.includes('❌') || ll.includes('falhou')) cls = 'log-err';
        else if (ll.includes('✅') || ll.includes('conclu') || ll.includes('sucesso')) cls = 'log-ok';
        else if (ll.includes('⚠') || ll.includes('aviso') || ll.includes('cancelado')) cls = 'log-warn';
        return `<div class="${cls}">${escHtml(l)}</div>`;
    }).join('');

    if (wasAtBottom || linhas.length < 5) {
        body.scrollTop = body.scrollHeight;
    }
}

// ════════════════════════════════════════════════════
// AÇÕES DA FILA
// ════════════════════════════════════════════════════
async function iniciarFila() {
    try {
        const r = await fetch('/api/fila/iniciar', { method: 'POST' });
        const d = await r.json();
        if (!d.success) { showToast('⚠️ ' + d.message, 'warn'); }
        else { showToast('▶ Fila iniciada!', 'ok'); }
    } catch(e) { showToast('❌ Erro de conexão', 'err'); }
}

async function pararFila() {
    try {
        await fetch('/api/fila/parar', { method: 'POST' });
        showToast('⏸ Sinal de parada enviado.', 'warn');
    } catch(e) { showToast('❌ Erro de conexão', 'err'); }
}

async function removerItem(idx) {
    try {
        await fetch('/api/fila/remover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idx })
        });
        if (selectedIdx === idx) selectedIdx = null;
    } catch(e) {}
}

async function removerSelecionado() {
    if (selectedIdx === null) { showToast('Selecione um item primeiro!', 'warn'); return; }
    await removerItem(selectedIdx);
    selectedIdx = null;
}

async function moverItemDireto(idx, direcao) {
    try {
        await fetch('/api/fila/reordenar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idx, direcao })
        });
    } catch(e) {}
}

async function moverItem(direcao) {
    if (selectedIdx === null) { showToast('Selecione um item primeiro!', 'warn'); return; }
    await moverItemDireto(selectedIdx, direcao);
    selectedIdx = Math.max(0, Math.min(filaData.length - 1, selectedIdx + direcao));
}

async function limparConcluidos() {
    try {
        const r = await fetch('/api/fila/limpar_concluidos', { method: 'POST' });
        const d = await r.json();
        showToast(`🧹 ${d.removidos} item(s) removido(s).`, 'ok');
    } catch(e) {}
}

// ════════════════════════════════════════════════════
// MODAL — ADICIONAR PROJETO
// ════════════════════════════════════════════════════
function openModalAdd() {
    document.getElementById('f-nome').value    = '';
    document.getElementById('f-audio').value   = '';
    document.getElementById('f-saida').value   = '';
    document.getElementById('f-musica').value  = '';
    document.getElementById('f-roteiro').value = '';
    openModal('modal-add');
}

async function confirmarAdd() {
    const audio = document.getElementById('f-audio').value.trim();
    if (!audio) { showToast('❌ Informe o caminho do áudio!', 'err'); return; }

    const payload = {
        nome:    document.getElementById('f-nome').value.trim(),
        audio,
        saida:   document.getElementById('f-saida').value.trim(),
        musica:  document.getElementById('f-musica').value.trim(),
        roteiro: document.getElementById('f-roteiro').value.trim(),
        perfil:  document.getElementById('f-perfil').value,
    };

    try {
        const r = await fetch('/api/fila/adicionar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const d = await r.json();
        if (d.success) {
            showToast(`✅ Projeto adicionado! (Total: ${d.total})`, 'ok');
            closeModal('modal-add');
        } else {
            showToast('❌ ' + d.error, 'err');
        }
    } catch(e) { showToast('❌ Erro de conexão', 'err'); }
}

// ════════════════════════════════════════════════════
// MODAL — ADICIONAR EM LOTE
// ════════════════════════════════════════════════════
function openModalLote() {
    document.getElementById('lote-audios').value = '';
    document.getElementById('lote-saida').value  = '';
    openModal('modal-lote');
}

async function confirmarLote() {
    const audiosRaw = document.getElementById('lote-audios').value;
    const audios = audiosRaw.split('\n').map(l => l.trim()).filter(Boolean);
    if (!audios.length) { showToast('❌ Informe pelo menos um áudio.', 'err'); return; }

    const saida  = document.getElementById('lote-saida').value.trim();
    const perfil = document.getElementById('lote-perfil').value;

    try {
        const r = await fetch('/api/fila/adicionar_lote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audios, saida, perfil })
        });
        const d = await r.json();
        if (d.success) {
            showToast(`✅ ${d.adicionados} projeto(s) adicionado(s)!`, 'ok');
            closeModal('modal-lote');
        } else {
            showToast('❌ Erro ao adicionar lote.', 'err');
        }
    } catch(e) { showToast('❌ Erro de conexão', 'err'); }
}

// ════════════════════════════════════════════════════
// HOT-FOLDER / PILOTO AUTOMÁTICO
// ════════════════════════════════════════════════════
function openHotfolderPanel() {
    const panel = document.getElementById('hotfolder-panel');
    panel.style.display = panel.style.display === 'none' ? 'flex' : 'none';
}

async function browsePastaHotfolder() {
    try {
        const r = await fetch('/api/browse_file?type=folder');
        const d = await r.json();
        if (d.status === 'success') {
            document.getElementById('hotfolder-path').value = d.path;
        }
    } catch(e) {}
}

async function ativarHotfolder() {
    const pasta = document.getElementById('hotfolder-path').value.trim();
    if (!pasta) { showToast('Selecione uma pasta primeiro!', 'warn'); return; }

    try {
        await fetch('/api/fila/hotfolder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pasta, ativo: true })
        });
        document.getElementById('btn-hf-ativar').style.display = 'none';
        document.getElementById('btn-hf-parar').style.display  = 'inline-flex';
        document.getElementById('toggle-hotfolder').classList.add('on');
        showToast('🤖 Piloto Automático ATIVO!', 'ok');
    } catch(e) { showToast('❌ Erro', 'err'); }
}

async function desativarHotfolder() {
    try {
        await fetch('/api/fila/hotfolder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pasta: '', ativo: false })
        });
        document.getElementById('btn-hf-ativar').style.display = 'inline-flex';
        document.getElementById('btn-hf-parar').style.display  = 'none';
        document.getElementById('toggle-hotfolder').classList.remove('on');
        showToast('🤖 Piloto Automático DESATIVADO.', 'warn');
    } catch(e) {}
}

function toggleTimeline(el) {
    el.classList.toggle('on');
    enviarTimeline = el.classList.contains('on');
}

// ════════════════════════════════════════════════════
// PERFIS
// ════════════════════════════════════════════════════
async function carregarPerfis() {
    try {
        const r = await fetch('/api/fila/perfis_diretor');
        const d = await r.json();
        const perfis = d.perfis || [];
        ['f-perfil', 'lote-perfil'].forEach(id => {
            const sel = document.getElementById(id);
            if (!sel) return;
            // Mantém a opção "(Nenhum)"
            while (sel.options.length > 1) sel.remove(1);
            perfis.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p; opt.textContent = p;
                sel.appendChild(opt);
            });
        });
    } catch(e) {}
}

// ════════════════════════════════════════════════════
// TABS
// ════════════════════════════════════════════════════
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`tab-${tab}-btn`).classList.add('active');
    document.getElementById(`tab-${tab}`).classList.add('active');
}

// ════════════════════════════════════════════════════
// UTILITÁRIOS
// ════════════════════════════════════════════════════
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

// Fecha modal ao clicar no overlay
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
        if (e.target === overlay) overlay.classList.remove('open');
    });
});

async function browseFile(inputId, type) {
    try {
        const r = await fetch(`/api/browse_file?type=${type}`);
        const d = await r.json();
        if (d.status === 'success') {
            document.getElementById(inputId).value = d.path;
        }
    } catch(e) { showToast('❌ Erro ao abrir seletor de arquivo', 'err'); }
}

function limparLog() {
    document.getElementById('log-body').innerHTML = '';
    ultimoLogCount = 0;
}

function escHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// ── Toast notifications
let toastTimeout = null;
function showToast(msg, type = 'ok') {
    let toast = document.getElementById('__toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = '__toast';
        toast.style.cssText = `
            position:fixed; bottom:24px; right:24px; z-index:9999;
            padding:10px 18px; border-radius:10px; font-size:13px; font-weight:600;
            box-shadow: 0 4px 20px rgba(0,0,0,.4); transition: opacity .3s;
            font-family: 'Inter', sans-serif;
        `;
        document.body.appendChild(toast);
    }
    const colors = {
        ok:   { bg: '#10b981', border: '#059669' },
        err:  { bg: '#ef4444', border: '#dc2626' },
        warn: { bg: '#f59e0b', border: '#d97706' },
    };
    const c = colors[type] || colors.ok;
    toast.style.background = c.bg;
    toast.style.border = `1px solid ${c.border}`;
    toast.style.color = '#fff';
    toast.style.opacity = '1';
    toast.textContent = msg;
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => { toast.style.opacity = '0'; }, 3500);
}
