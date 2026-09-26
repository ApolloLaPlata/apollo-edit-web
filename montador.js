/**
 * montador.js — Lógica do Montador (Transições e Logomarcas)
 * Apollo Studio Web UI
 */

// ── Estado
const state = {
    videos: [],          // [{path, nome, duracao}]
    formato: 'vertical',
    usar_transicao: true,
    usar_cta: false,
    usar_logomarca: false,
    processando: false,
};
let cacheDebounceTimer = null;

// ── Init
document.addEventListener('DOMContentLoaded', () => {
    carregarCache();
});

// ════════════════════════════════════════════════════
// SELEÇÃO DE VÍDEOS
// ════════════════════════════════════════════════════
async function adicionarVideos() {
    // Usa o browse_file do servidor mas em loop para simular seleção múltipla
    // Primeiro pede quantos e depois abre seletor para cada um
    // Estratégia: abrir seletor 1x por clique, usuário pode clicar várias vezes
    try {
        const r = await fetch('/api/browse_file?type=file');
        const d = await r.json();
        if (d.status === 'success' && d.path) {
            const caminho = d.path;
            // Evita duplicatas
            if (state.videos.some(v => v.path === caminho)) {
                showToast('⚠️ Este vídeo já está na lista.', 'warn');
                return;
            }
            const nome = caminho.split(/[/\\]/).pop();
            state.videos.push({ path: caminho, nome });
            renderVideoList();
            showToast(`✅ Vídeo adicionado: ${nome}`, 'ok');
        }
    } catch(e) {
        showToast('❌ Erro ao abrir seletor de arquivo', 'err');
    }
}

function renderVideoList() {
    const list = document.getElementById('video-list');
    const empty = document.getElementById('empty-drop');
    const countBadge = document.getElementById('video-count');

    countBadge.textContent = state.videos.length;

    // Remove itens antigos (mas mantém o empty-drop)
    Array.from(list.children).forEach(c => {
        if (c.id !== 'empty-drop') c.remove();
    });

    if (state.videos.length === 0) {
        empty.style.display = 'flex';
        updateStatus('Aguardando seleção de vídeos...');
        return;
    }

    empty.style.display = 'none';

    state.videos.forEach((v, idx) => {
        const item = document.createElement('div');
        item.className = 'video-item';
        item.innerHTML = `
            <div class="video-thumb" id="thumb-${idx}">🎞️</div>
            <div class="video-info">
                <div class="video-name" title="${escHtml(v.path)}">${escHtml(v.nome)}</div>
                <div class="video-meta">${escHtml(v.path)}</div>
            </div>
            <button class="video-remove" onclick="removerVideo(${idx})" title="Remover da lista">✕</button>
        `;
        list.appendChild(item);

        // Tenta carregar thumbnail via API
        carregarThumb(idx, v.path);
    });

    updateStatus(`${state.videos.length} vídeo(s) selecionado(s). Pronto para processar.`);
}

async function carregarThumb(idx, videoPath) {
    try {
        const r = await fetch(`/api/thumb?path=${encodeURIComponent(videoPath)}`);
        if (r.ok && r.status !== 501) {
            const blob = await r.blob();
            if (blob.type.startsWith('image/')) {
                const url = URL.createObjectURL(blob);
                const el = document.getElementById(`thumb-${idx}`);
                if (el) {
                    el.innerHTML = `<img src="${url}" alt="thumb">`;
                }
            }
        }
    } catch(e) {}
}

function removerVideo(idx) {
    state.videos.splice(idx, 1);
    renderVideoList();
}

function limparSelecao() {
    if (state.videos.length === 0) return;
    if (!confirm(`Remover todos os ${state.videos.length} vídeo(s) da lista?`)) return;
    state.videos = [];
    renderVideoList();
}

// ════════════════════════════════════════════════════
// FORMATO
// ════════════════════════════════════════════════════
function setFormato(fmt) {
    state.formato = fmt;
    document.getElementById('fmt-v').classList.toggle('active', fmt === 'vertical');
    document.getElementById('fmt-h').classList.toggle('active', fmt === 'horizontal');
}

// ════════════════════════════════════════════════════
// CHECKBOXES DE SEQUÊNCIA
// ════════════════════════════════════════════════════
function toggleCheck(elId, stateKey) {
    const el = document.getElementById(elId);
    el.classList.toggle('checked');
    const isChecked = el.classList.contains('checked');
    el.querySelector('.check-box').textContent = isChecked ? '✓' : '';
    state[stateKey] = isChecked;
}

// ════════════════════════════════════════════════════
// PASTAS — Browse + Cache
// ════════════════════════════════════════════════════
async function browsePasta(inputId) {
    try {
        const r = await fetch('/api/browse_file?type=folder');
        const d = await r.json();
        if (d.status === 'success') {
            document.getElementById(inputId).value = d.path;
            salvarCacheDebounce();
        }
    } catch(e) { showToast('❌ Erro ao abrir seletor', 'err'); }
}

async function carregarCache() {
    try {
        const r = await fetch('/api/montador/cache');
        const d = await r.json();
        if (d.success && d.cache) {
            const c = d.cache;
            ['pasta_trans_h','pasta_trans_v','pasta_cta_h','pasta_cta_v','pasta_logo_h','pasta_logo_v'].forEach(id => {
                const el = document.getElementById(id);
                if (el && c[id]) el.value = c[id];
            });
        }
    } catch(e) {}
}

function salvarCacheDebounce() {
    clearTimeout(cacheDebounceTimer);
    cacheDebounceTimer = setTimeout(salvarCache, 800);
}

async function salvarCache() {
    const cache = {};
    ['pasta_trans_h','pasta_trans_v','pasta_cta_h','pasta_cta_v','pasta_logo_h','pasta_logo_v'].forEach(id => {
        cache[id] = document.getElementById(id)?.value || '';
    });
    try {
        await fetch('/api/montador/cache', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cache)
        });
    } catch(e) {}
}

// ════════════════════════════════════════════════════
// VERIFICAR PASTAS
// ════════════════════════════════════════════════════
async function verificarPastas() {
    const ids = ['pasta_trans_h','pasta_trans_v','pasta_cta_h','pasta_cta_v','pasta_logo_h','pasta_logo_v'];
    const params = new URLSearchParams();
    ids.forEach(id => params.append(id, document.getElementById(id)?.value || ''));

    const info = document.getElementById('pasta-info');
    info.innerHTML = '<span style="color:var(--muted)">Verificando...</span>';

    try {
        const r = await fetch('/api/montador/verificar_pastas?' + params.toString());
        const d = await r.json();
        if (!d.success) {
            info.innerHTML = '<span class="pi-err">❌ Erro ao verificar pastas.</span>';
            return;
        }
        let html = '';
        for (const [key, p] of Object.entries(d.pastas)) {
            if (p.status === 'ok') {
                html += `<div class="pi-ok">✅ ${p.label}: ${p.count} arquivo(s)</div>`;
            } else if (p.status === 'vazia') {
                html += `<div class="pi-vaz">⚠️ ${p.label}: pasta vazia (0 mp4s)</div>`;
            } else if (p.status === 'nao_encontrada') {
                html += `<div class="pi-err">❌ ${p.label}: pasta não encontrada</div>`;
            } else {
                html += `<div class="pi-nop">⚪ ${p.label}: não configurada</div>`;
            }
        }
        info.innerHTML = html || '<span style="color:var(--muted)">Nenhuma pasta configurada.</span>';
    } catch(e) {
        info.innerHTML = '<span class="pi-err">❌ Erro de conexão com o servidor.</span>';
    }
}

// ════════════════════════════════════════════════════
// PROCESSAMENTO
// ════════════════════════════════════════════════════
async function processarVideos() {
    if (state.videos.length === 0) {
        showToast('⚠️ Selecione pelo menos um vídeo!', 'warn');
        return;
    }
    if (!state.usar_transicao && !state.usar_cta && !state.usar_logomarca) {
        showToast('⚠️ Marque pelo menos uma opção da sequência!', 'warn');
        return;
    }

    // Salva cache antes de processar
    await salvarCache();

    const payload = {
        videos: state.videos.map(v => v.path),
        formato: state.formato,
        usar_transicao: state.usar_transicao,
        usar_cta: state.usar_cta,
        usar_logomarca: state.usar_logomarca,
        pasta_trans_h: document.getElementById('pasta_trans_h')?.value || '',
        pasta_trans_v: document.getElementById('pasta_trans_v')?.value || '',
        pasta_cta_h:   document.getElementById('pasta_cta_h')?.value   || '',
        pasta_cta_v:   document.getElementById('pasta_cta_v')?.value   || '',
        pasta_logo_h:  document.getElementById('pasta_logo_h')?.value  || '',
        pasta_logo_v:  document.getElementById('pasta_logo_v')?.value  || '',
    };

    // UI de loading
    document.getElementById('btn-processar').disabled = true;
    document.getElementById('status-badge').textContent = '🔄 Processando...';
    document.getElementById('status-badge').style.color = '#06b6d4';
    updateStatus('Iniciando processamento...');
    clearLog();
    appendLog('🚀 Enviando requisição ao servidor...');
    document.getElementById('progress-fill').style.width = '5%';

    state.processando = true;

    try {
        const r = await fetch('/api/montador/processar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!r.ok) {
            appendLog(`❌ Erro HTTP: ${r.status}`, 'le');
            finalizarProcessamento(false);
            return;
        }

        // Lê o stream SSE
        const reader = r.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // guarda linha incompleta
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const msg = line.slice(6);
                    if (msg === '__DONE__') {
                        finalizarProcessamento(true);
                        return;
                    }
                    // Classifica a linha
                    let cls = '';
                    const ml = msg.toLowerCase();
                    if (ml.includes('❌') || ml.includes('erro') || ml.includes('falha')) cls = 'le';
                    else if (ml.includes('✅') || ml.includes('conclu') || ml.includes('sucesso')) cls = 'lo';
                    else if (ml.includes('⚠') || ml.includes('aviso')) cls = 'lw';
                    appendLog(msg, cls);

                    // Update status da linha
                    updateStatus(msg.replace(/[🚀🎬✅❌⚠️📎✓⚙️]/g, '').trim());
                    // Update progress bar via polling
                    atualizarProgresso();
                }
            }
        }
        finalizarProcessamento(true);
    } catch(e) {
        appendLog(`❌ Erro de conexão: ${e}`, 'le');
        finalizarProcessamento(false);
    }
}

async function atualizarProgresso() {
    try {
        const r = await fetch('/api/montador/status');
        const d = await r.json();
        if (d.progresso !== undefined) {
            document.getElementById('progress-fill').style.width = d.progresso + '%';
        }
    } catch(e) {}
}

function finalizarProcessamento(sucesso) {
    state.processando = false;
    document.getElementById('btn-processar').disabled = false;
    document.getElementById('progress-fill').style.width = sucesso ? '100%' : '0%';
    document.getElementById('status-badge').textContent = sucesso ? '✅ Concluído' : '❌ Erro';
    document.getElementById('status-badge').style.color = sucesso ? '#10b981' : '#ef4444';
    if (sucesso) {
        updateStatus(`✅ Processamento concluído com sucesso!`);
        if (window.apolloTransferOS) {
            window.apolloTransferOS.addItem('video', 'lote_processado.mp4', 'Montador de Clipes', null, { url: '/test.mp4' });
        }
        showToast('✅ Vídeos processados e enviados ao Bagageiro!', 'ok');
    } else {
        updateStatus('❌ Houve erros durante o processamento. Verifique o log.');
        showToast('❌ Erros durante o processamento.', 'err');
    }
    // Reseta badge após 5s
    setTimeout(() => {
        document.getElementById('status-badge').textContent = 'Pronto';
        document.getElementById('status-badge').style.color = '';
    }, 5000);
}

// ════════════════════════════════════════════════════
// LOG
// ════════════════════════════════════════════════════
function appendLog(msg, cls = '') {
    const body = document.getElementById('log-body');
    // Remove placeholder
    const placeholder = body.querySelector('span[style]');
    if (placeholder) placeholder.remove();

    const div = document.createElement('div');
    if (cls) div.className = cls;
    div.textContent = msg;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

function clearLog() {
    const body = document.getElementById('log-body');
    body.innerHTML = '';
}

function limparLog() {
    clearLog();
}

// ════════════════════════════════════════════════════
// UTILITÁRIOS
// ════════════════════════════════════════════════════
function updateStatus(msg) {
    document.getElementById('status-line').textContent = msg;
}

function escHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

let _toastTimer = null;
function showToast(msg, type = 'ok') {
    let el = document.getElementById('__toast');
    if (!el) {
        el = document.createElement('div');
        el.id = '__toast';
        el.style.cssText = `position:fixed;bottom:24px;right:24px;z-index:9999;padding:10px 18px;
            border-radius:10px;font-size:13px;font-weight:600;box-shadow:0 4px 20px rgba(0,0,0,.4);
            transition:opacity .3s;font-family:'Inter',sans-serif;`;
        document.body.appendChild(el);
    }
    const c = { ok: ['#10b981','#059669'], err: ['#ef4444','#dc2626'], warn: ['#f59e0b','#d97706'] }[type] || ['#10b981','#059669'];
    el.style.background = c[0]; el.style.border = `1px solid ${c[1]}`; el.style.color = '#fff';
    el.style.opacity = '1'; el.textContent = msg;
    clearTimeout(_toastTimer);
    _toastTimer = setTimeout(() => { el.style.opacity = '0'; }, 3500);
}
