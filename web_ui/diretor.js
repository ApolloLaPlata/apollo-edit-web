document.addEventListener('DOMContentLoaded', () => {
    loadProfiles();
    loadPerfisDiretor();
    loadPerfisEstetica();
    loadPerfisLegenda();
    loadPerfisTransicaoTemplate();
    toggleMappingMode();
    toggleRoteiroBase();
    toggleModoRitmo();
});

// -- FUNÇÕES DE MODO / TOGGLE --
function toggleMappingMode() {
    const isMapped = document.getElementById('usar_mapeamento').checked;
    const singleProfileBox = document.getElementById('single_profile_box');
    const sectionRoteiroGrafico = document.getElementById('section_roteiro_grafico');

    if (isMapped) {
        singleProfileBox.style.opacity = '0.5';
        singleProfileBox.style.pointerEvents = 'none';
        sectionRoteiroGrafico.style.opacity = '1';
        sectionRoteiroGrafico.style.pointerEvents = 'all';
    } else {
        singleProfileBox.style.opacity = '1';
        singleProfileBox.style.pointerEvents = 'all';
        sectionRoteiroGrafico.style.opacity = '0.5';
        sectionRoteiroGrafico.style.pointerEvents = 'none';
    }
}

function toggleRoteiroBase() {
    const isRoteiroBase = document.getElementById('usar_roteiro_base').checked;
    const txtBase = document.getElementById('text_map_base');
    
    if (isRoteiroBase) {
        txtBase.style.opacity = '1';
        txtBase.readOnly = false;
    } else {
        txtBase.style.opacity = '0.5';
        txtBase.readOnly = true;
    }
}

function toggleModoRitmo() {
    const modo = document.querySelector('input[name="modo_ritmo"]:checked').value;
    const btnProcurarAudio = document.querySelector('button[onclick*="audio_path"]');
    const inputAudio = document.getElementById('audio_path');
    
    if (modo === 'lipsync') {
        if(inputAudio) inputAudio.disabled = true;
        if(btnProcurarAudio) btnProcurarAudio.disabled = true;
        // Força sincronização base a ser ativada na UI se existir
        const syncBase = document.getElementById('sincronizar_base');
        if (syncBase) syncBase.checked = true;
    } else {
        if(inputAudio) inputAudio.disabled = false;
        if(btnProcurarAudio) btnProcurarAudio.disabled = false;
    }
}

// -- INTEGRAÇÃO COM BACKEND --
async function loadProfiles() {
    const select = document.getElementById('perfil_unico');
    select.innerHTML = '<option value="">Carregando perfis...</option>';
    
    try {
        const response = await fetch('https://api.apolloedit.com/api/list_profiles');
        const result = await response.json();
        
        if (result.status === 'success') {
            select.innerHTML = '';
            if (result.profiles.length === 0) {
                select.innerHTML = '<option value="">Nenhum perfil encontrado</option>';
            } else {
                result.profiles.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p;
                    opt.textContent = p;
                    select.appendChild(opt);
                });
            }
        }
    } catch (e) {
        select.innerHTML = '<option value="">Erro ao carregar</option>';
        logTerminal(`Erro ao carregar perfis: ${e.message}`, 'error');
    }
}

// -- PERFIS (Diretor, Estética, Legenda) --
async function _loadGenericProfiles(endpoint, selectId, defaultText) {
    const select = document.getElementById(selectId);
    if (!select) return;
    try {
        const response = await fetch(endpoint);
        const result = await response.json();
        select.innerHTML = `<option value="">${defaultText}</option>`;
        if (result.status === 'success' && result.perfis) {
            result.perfis.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p;
                opt.textContent = p;
                select.appendChild(opt);
            });
        }
    } catch (e) {
        console.error("Erro carregando", selectId, e);
    }
}

function loadPerfisDiretor() { _loadGenericProfiles('/api/diretor/perfis_diretor', 'perfil_diretor', 'Selecione um Perfil...'); }
function loadPerfisEstetica() { _loadGenericProfiles('/api/diretor/perfis_estetica', 'perfil_estetica', '[Personalizado]'); }
function loadPerfisLegenda() { _loadGenericProfiles('/api/diretor/perfis_legenda', 'perfil_legenda', '[Personalizado]'); }
function loadPerfisTransicaoTemplate() { _loadGenericProfiles('/api/diretor/perfis_transicao_template', 'transicao_template', '[Corte Seco]'); }

async function salvarPerfilDiretor() {
    const nome = prompt("Nome do Perfil do Diretor:");
    if (!nome) return;
    try {
        await fetch('https://api.apolloedit.com/api/diretor/perfis_diretor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome: nome, config: getPayload() })
        });
        loadPerfisDiretor();
        logTerminal(`Perfil de diretor '${nome}' salvo.`, 'success');
    } catch (e) { logTerminal('Erro ao salvar perfil.', 'error'); }
}

async function deletarPerfilDiretor() {
    const select = document.getElementById('perfil_diretor');
    const nome = select.value;
    if (!nome) return;
    if (!confirm(`Deletar perfil '${nome}'?`)) return;
    try {
        await fetch('https://api.apolloedit.com/api/diretor/perfis_diretor', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome: nome })
        });
        loadPerfisDiretor();
        logTerminal(`Perfil '${nome}' deletado.`, 'warning');
    } catch (e) { logTerminal('Erro ao deletar perfil.', 'error'); }
}

function aplicarPerfilEstetica() {
    logTerminal("O perfil estético será processado no backend.", "info");
}

function aplicarPerfilLegenda() {
    logTerminal("O perfil de legenda será processado no backend.", "info");
}

function aplicarTransicaoTemplate() {
    logTerminal("A transição entre templates será processada no backend.", "info");
}

function limparCacheWhisper() {
    fetch('https://api.apolloedit.com/api/whisper/limpar_cache', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') logTerminal("Cache do Whisper (temp_audio) limpo com sucesso!", "success");
            else logTerminal("Erro ao limpar cache.", "error");
        });
}

async function browseFile(inputId, type = 'media') {
    try {
        // Usar endpoint genérico browse_file (ou criar um novo no python futuramente)
        const response = await fetch('https://api.apolloedit.com/api/browse_file', { method: 'POST' });
        const result = await response.json();
        if (result.status === 'success' && result.path) {
            document.getElementById(inputId).value = result.path;
            logTerminal(`Arquivo selecionado: ${result.path}`, 'info');
        }
    } catch (e) {
        logTerminal(`Erro ao buscar arquivo: ${e.message}`, 'error');
    }
}

async function browseFolder(inputId) {
    try {
        // Fallback: se o servidor não tiver browse_folder, pode falhar.
        const response = await fetch('https://api.apolloedit.com/api/browse_file?type=folder', { method: 'POST' });
        const result = await response.json();
        if (result.status === 'success' && result.path) {
            // Em Python filedialog.askdirectory deve ser implementado no backend
            document.getElementById(inputId).value = result.path;
            logTerminal(`Pasta selecionada: ${result.path}`, 'info');
        }
    } catch (e) {
        logTerminal("Por favor atualize o backend para suportar seleção de pastas (browse_folder).", 'warning');
    }
}

// -- VÍDEOS BASE --
let videoList = [];

function addVideos() {
    // Simula seleção múltipla e adiciona na lista
    fetch('https://api.apolloedit.com/api/browse_file')
        .then(res => res.json())
        .then(result => {
            if (result.status === 'success' && result.path) {
                if (!videoList.includes(result.path)) {
                    videoList.push(result.path);
                    renderVideoGrid();
                    logTerminal(`Vídeo base adicionado: ${result.path.split(/[\/\\]/).pop()}`, 'info');
                }
            }
        });
}

function removeSelectedVideos() {
    const selected = document.querySelectorAll('.video-item.selected');
    selected.forEach(el => {
        const path = el.getAttribute('data-path');
        videoList = videoList.filter(p => p !== path);
    });
    renderVideoGrid();
    logTerminal(`${selected.length} vídeos removidos.`, 'warning');
}

function limparTodosVideos() {
    videoList = [];
    renderVideoGrid();
    logTerminal(`Todos os vídeos foram removidos.`, 'warning');
}

function renderVideoGrid() {
    const grid = document.getElementById('video_grid');
    const badge = document.getElementById('video-count');
    
    badge.textContent = `${videoList.length} vídeos`;
    
    if (videoList.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <span class="icon">📂</span>
                <p>Nenhum vídeo adicionado.</p>
                <p class="sub">Arraste arquivos ou clique em Adicionar.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = '';
    videoList.forEach((path, index) => {
        const filename = path.split(/[\/\\]/).pop();
        const div = document.createElement('div');
        div.className = 'video-item';
        div.setAttribute('data-path', path);
        
        // Exibe um thumb vazio até o backend carregar (usando endpoint /api/thumb)
        div.innerHTML = `
            <div class="idx">${index + 1}</div>
            <img class="thumb" src="/api/thumb?path=${encodeURIComponent(path)}" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNjAiIGhlaWdodD0iOTAiPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiMzMzQiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZmlsbD0iI2ZmZiIgZHk9Ii4zZW0iIHRleHQtYW5jaG9yPSJtaWRkbGUiPk5vIFRodW1iPC90ZXh0Pjwvc3ZnPg=='">
            <div class="info">
                <div class="name" title="${filename}">${filename}</div>
            </div>
        `;
        
        div.addEventListener('click', () => {
            div.classList.toggle('selected');
        });
        
        grid.appendChild(div);
    });
}

function moveVideoUp() {
    const grid = document.getElementById('video_grid');
    const selected = grid.querySelector('.video-item.selected');
    if (!selected) return;
    
    const path = selected.getAttribute('data-path');
    const idx = videoList.indexOf(path);
    if (idx > 0) {
        [videoList[idx - 1], videoList[idx]] = [videoList[idx], videoList[idx - 1]];
        renderVideoGrid();
        // Restaurar seleção
        setTimeout(() => {
            const el = document.querySelector(`.video-item[data-path="${path}"]`);
            if (el) el.classList.add('selected');
        }, 50);
    }
}

function moveVideoDown() {
    const grid = document.getElementById('video_grid');
    const selected = grid.querySelector('.video-item.selected');
    if (!selected) return;
    
    const path = selected.getAttribute('data-path');
    const idx = videoList.indexOf(path);
    if (idx < videoList.length - 1 && idx !== -1) {
        [videoList[idx + 1], videoList[idx]] = [videoList[idx], videoList[idx + 1]];
        renderVideoGrid();
        setTimeout(() => {
            const el = document.querySelector(`.video-item[data-path="${path}"]`);
            if (el) el.classList.add('selected');
        }, 50);
    }
}

// -- TERMINAL & LOGS --
function logTerminal(message, type = 'info') {
    const consoleLog = document.getElementById('console_log');
    const div = document.createElement('div');
    div.className = `log-line ${type}`;
    const time = new Date().toLocaleTimeString();
    div.textContent = `[${time}] ${message}`;
    consoleLog.appendChild(div);
    consoleLog.scrollTop = consoleLog.scrollHeight;
}

function clearLogs() {
    document.getElementById('console_log').innerHTML = '';
}

// -- INICIAR RENDER --
document.getElementById('btn-render-master').addEventListener('click', () => {
    const audioPath = document.getElementById('audio_path').value;
    const saidaDir = document.getElementById('saida_dir').value;
    
    if (!audioPath || !saidaDir) {
        logTerminal("Erro: Selecione o Áudio Narração e a Pasta de Saída.", "error");
        alert("Preencha as Entradas e Saídas necessárias!");
        return;
    }
    
    logTerminal("Iniciando requisição de Renderização em Lote...", "info");
    
    
    // Obter dados do Form
    function getPayload() {
        return {
        audio_path: document.getElementById('audio_path').value,
        saida_dir: document.getElementById('saida_dir').value,
        video_format: document.querySelector('input[name="video_format"]:checked').value,
        musica_path: document.getElementById('musica_path').value,
        vol_musica: document.getElementById('vol_musica').value,
        
        master_hd: document.getElementById('master_hd').checked,
        master_overlay: document.getElementById('master_overlay').checked,
        master_xfade: document.getElementById('master_xfade').checked,
        master_lut: document.getElementById('master_lut').checked,
        master_cor: document.getElementById('master_cor').checked,
        master_cam: document.getElementById('master_cam').checked,
        prob_transicao: document.getElementById('prob_transicao').value,
        
        var_legenda: document.getElementById('var_legenda').checked,
        legenda_cfg: {
            font: document.getElementById('sub_font').value,
            words: document.getElementById('sub_words').value,
            pos: document.getElementById('sub_pos').value,
            theme: document.getElementById('sub_theme').value,
            size: document.getElementById('sub_size').value,
            margin_v: document.getElementById('sub_margin_v').value,
            effect: document.getElementById('sub_effect').value,
            mapa_temas_path: document.getElementById('mapa_temas_path').value
        },
        
        variaveis_globais: {
            narrador: document.getElementById('lay2_narrador_path').value,
            frente: document.getElementById('lay3_frente_path').value,
            moldura_dir: document.getElementById('lay4_moldura_dir').value,
        },
        
        usar_mapeamento: document.getElementById('usar_mapeamento').checked,
        perfil_unico: document.getElementById('perfil_unico').value,
        
        roteiro_base: document.getElementById('usar_roteiro_base').checked ? document.getElementById('text_map_base').value : "",
        roteiro_grafico: document.getElementById('text_mapeamento').value,
        
        videos_base: videoList,
        sincronizar_base: document.getElementById('sincronizar_base').checked,
        base_loop_count: document.getElementById('base_loop_count').value,
        tipo_midia_upload: document.getElementById('tipo_midia_upload') ? document.getElementById('tipo_midia_upload').value : "Fotos e Vídeos",
        
        perfil_diretor: document.getElementById('perfil_diretor') ? document.getElementById('perfil_diretor').value : "",
        perfil_estetica: document.getElementById('perfil_estetica') ? document.getElementById('perfil_estetica').value : "",
        perfil_legenda: document.getElementById('perfil_legenda') ? document.getElementById('perfil_legenda').value : "",
        transicao_template: document.getElementById('transicao_template') ? document.getElementById('transicao_template').value : "[Corte Seco]",
        modo_ritmo: document.querySelector('input[name="modo_ritmo"]:checked') ? document.querySelector('input[name="modo_ritmo"]:checked').value : "tts",
        enviar_timeline: document.getElementById('enviar_timeline') ? document.getElementById('enviar_timeline').checked : true
    };
    return payload;
}

document.getElementById('btn-render-master').addEventListener('click', () => {
    const payload = getPayload();
    if (!payload.audio_path || !payload.saida_dir) {
        if (payload.modo_ritmo !== 'lipsync' && !payload.audio_path) {
            logTerminal("Erro: Selecione o Áudio Narração e a Pasta de Saída.", "error");
            alert("Preencha as Entradas e Saídas necessárias!");
            return;
        } else if (!payload.saida_dir) {
            logTerminal("Erro: Selecione a Pasta de Saída.", "error");
            alert("Preencha a Pasta de Saída!");
            return;
        }
    }
    
    logTerminal("Iniciando requisição de Renderização em Lote...", "info");
    console.log("Payload Render:", payload);
    logTerminal("Enviando requisição para o servidor Python...", "info");
    
    document.getElementById('btn-render-master').disabled = true;
    const text = document.getElementById('render_status_text');
    text.textContent = "Na Fila...";
    
    fetch('https://api.apolloedit.com/api/render_diretor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            logTerminal("✅ " + data.message + ` (Posição na fila: ${data.queue_position})`, "success");
            text.textContent = "Enviado para a Fila!";
        } else {
            logTerminal("❌ Erro na requisição: " + data.message, "error");
            text.textContent = "Erro!";
        }
    })
    })
    .finally(() => {
        setTimeout(() => {
            document.getElementById('btn-render-master').disabled = false;
            text.textContent = "Renderizar Lote";
        }, 3000);
    });
});

// -- LÓGICA DO TANQUE DE COMBUSTÍVEL FRAGMENTADO (API MIX) --
document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('fuel-tank-dropzone');
    const bar = document.getElementById('fuel-tank-bar');
    const legend = document.getElementById('fuel-tank-legend');
    if (!dropzone || !bar || !legend) return;

    let tankSegments = []; // Array of { name: 'Flux', color: '#3B82F6', weight: 1 }

    // Permitir drop nativo (se o transfer_hud.js não interceptar tudo globalmente)
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('glow-green-target');
        dropzone.style.borderColor = '#4CAF50';
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = 'rgba(255, 255, 255, 0.2)';
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'rgba(255, 255, 255, 0.2)';
        
        // Em transfer_hud.js, os blocos têm class="transfer-item" e data-type
        const data = e.dataTransfer.getData('text/plain');
        try {
            const itemData = JSON.parse(data);
            if (itemData.type === 'api_consumable') {
                addConsumableToTank(itemData.name, itemData.color || '#F59E0B');
            } else {
                logTerminal('Apenas "Quadradinhos de API" podem ser colocados no Tanque.', 'warning');
            }
        } catch (err) {
            logTerminal('Item inválido arrastado para o Tanque.', 'error');
        }
    });

    function addConsumableToTank(name, color) {
        // Remove empty state text
        const emptyState = bar.querySelector('.fuel-empty');
        if (emptyState) emptyState.remove();

        tankSegments.push({ name, color, weight: 1 });
        renderTank();
        logTerminal(`[API Mix] ${name} adicionado ao roteamento.`, 'info');
    }

    function renderTank() {
        bar.innerHTML = '';
        legend.innerHTML = '';
        
        if (tankSegments.length === 0) {
            bar.innerHTML = '<div class="fuel-empty" style="flex-grow: 1; text-align: center; color: #555; font-size: 11px; line-height: 30px; letter-spacing: 1px;">VAZIO (NECESSITA COMBUSTÍVEL)</div>';
            return;
        }

        const totalWeight = tankSegments.reduce((sum, seg) => sum + seg.weight, 0);

        tankSegments.forEach((seg, index) => {
            // Render Segment in Bar
            const div = document.createElement('div');
            div.style.backgroundColor = seg.color;
            div.style.height = '100%';
            div.style.flexGrow = seg.weight;
            div.style.transition = 'flex-grow 0.3s ease';
            div.title = seg.name;
            bar.appendChild(div);

            // Render Legend Item
            const legDiv = document.createElement('div');
            legDiv.style.display = 'flex';
            legDiv.style.alignItems = 'center';
            legDiv.style.gap = '5px';
            legDiv.innerHTML = `
                <div style="width:12px; height:12px; background:${seg.color}; border-radius:2px;"></div>
                <span>${seg.name}</span>
                <button onclick="removeTankSegment(${index})" style="background:none; border:none; color:#FF5252; cursor:pointer; font-size:10px; margin-left:3px;">✖</button>
            `;
            legend.appendChild(legDiv);
        });
    }

    // Export remove to global scope for the inline onclick handler
    window.removeTankSegment = function(index) {
        tankSegments.splice(index, 1);
        renderTank();
        logTerminal(`[API Mix] Item removido do tanque.`, 'warning');
    };
});
