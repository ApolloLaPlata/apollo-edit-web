document.addEventListener('DOMContentLoaded', () => {
    loadProfiles();
    toggleMappingMode();
    toggleRoteiroBase();
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

// -- INTEGRAÇÃO COM BACKEND --
async function loadProfiles() {
    const select = document.getElementById('perfil_unico');
    select.innerHTML = '<option value="">Carregando perfis...</option>';
    
    try {
        const response = await fetch('/api/list_profiles');
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

async function browseFile(inputId, type = 'media') {
    try {
        // Usar endpoint genérico browse_file (ou criar um novo no python futuramente)
        const response = await fetch('/api/browse_file', { method: 'POST' });
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
        const response = await fetch('/api/browse_file?type=folder', { method: 'POST' });
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
    fetch('/api/browse_file')
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
    const payload = {
        audio_path: audioPath,
        saida_dir: saidaDir,
        video_format: document.querySelector('input[name="video_format"]:checked').value,
        musica_path: document.getElementById('musica_path').value,
        vol_musica: document.getElementById('vol_musica').value,
        
        usar_transicoes_hd: document.getElementById('usar_transicoes_hd').checked,
        usar_transicoes_ffmpeg: document.getElementById('usar_transicoes_ffmpeg').checked,
        usar_filtros_luz: document.getElementById('usar_filtros_luz').checked,
        prob_transicao: document.getElementById('prob_transicao').value,
        
        var_legenda: document.getElementById('var_legenda').checked,
        legenda_cfg: {
            font: document.getElementById('sub_font').value,
            words: document.getElementById('sub_words').value,
            pos: document.getElementById('sub_pos').value,
            theme: document.getElementById('sub_theme').value,
            size: document.getElementById('sub_size').value,
            margin_v: document.getElementById('sub_margin_v').value,
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
        base_loop_count: document.getElementById('base_loop_count').value
    };
    
    console.log("Payload Render:", payload);
    logTerminal("Pre-processamento e Whisper inicializados (Simulação).", "info");
    
    // Simulação de Progresso
    let progress = 0;
    const bar = document.getElementById('render_progress');
    const text = document.getElementById('render_status_text');
    
    document.getElementById('btn-render-master').disabled = true;
    
    const interval = setInterval(() => {
        progress += Math.floor(Math.random() * 15);
        if (progress > 100) progress = 100;
        
        bar.style.width = `${progress}%`;
        text.textContent = `Renderizando... ${progress}%`;
        
        if (progress === 100) {
            clearInterval(interval);
            logTerminal("✅ Renderização Concluída com Sucesso!", "success");
            text.textContent = "Concluído!";
            document.getElementById('btn-render-master').disabled = false;
        }
    }, 1000);
});
