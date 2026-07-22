/**
 * Apollo Flow Logic v1.0
 * Gerador de Imagens/Vídeos em Lote e Geração Rápida
 */

// =========================================
// ESTADO GLOBAL DO FLOW
// =========================================
const FlowState = {
    mode: 'studio',        // 'studio' | 'quickgen'
    scenes: [],            // Array de objetos de cena
    variations: 2,         // Quantidade de variações por cena
    activeStyle: 'Cinematográfico',
    referenceImage: null,  // Base64 da imagem de referência
    results: [],           // Array de resultados gerados
    activeJobs: {},        // { job_id: {sceneIndex, variation, status} }
    quickEngine: 'flux',   // Motor selecionado no modo rápido
    currentModalResult: null,  // Resultado aberto no modal
};

// Custo em Cristais por motor
const ENGINE_COSTS = {
    'flux': 1, 'flux-pro': 3,
    'hailuo': 5, 'ltx': 4, 'wan': 6, 'kling': 5
};
const ENGINE_LABELS = {
    'flux': '⚡ Flux 1.1', 'flux-pro': '⚡ Flux Pro',
    'hailuo': '🌊 Hailuo', 'ltx': '🎬 LTX-Video',
    'wan': '🔥 WAN 2.2', 'kling': '✨ Kling'
};

// URL do nosso Maestro backend
const MAESTRO_URL = 'http://localhost:3000';

// =========================================
// INICIALIZAÇÃO
// =========================================
document.addEventListener('DOMContentLoaded', () => {
    // Cena inicial padrão
    addScene();
    updateIgniteCost();
    
    // Simula carregar dados do usuário (Supabase/Auth)
    loadUserData();
});

function loadUserData() {
    // Integração futura com auth.js / laplata_db.js
    const mockCrystals = Math.floor(Math.random() * 400) + 100;
    const crystalEl = document.getElementById('user-crystals');
    if (crystalEl) crystalEl.textContent = mockCrystals;
}

// =========================================
// TROCA DE MODO (Studio / Geração Rápida)
// =========================================
function switchMode(mode) {
    FlowState.mode = mode;
    
    document.getElementById('mode-studio').style.display = mode === 'studio' ? 'grid' : 'none';
    document.getElementById('mode-quickgen').style.display = mode === 'quickgen' ? 'flex' : 'none';
    
    document.getElementById('tab-studio').classList.toggle('active', mode === 'studio');
    document.getElementById('tab-quickgen').classList.toggle('active', mode === 'quickgen');
}

// =========================================
// REFERENCE IMAGE
// =========================================
function handleRefUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        FlowState.referenceImage = e.target.result;
        document.getElementById('ref-preview').src = e.target.result;
        document.getElementById('ref-preview').style.display = 'block';
        document.getElementById('ref-placeholder').style.display = 'none';
        showToast('✅ Imagem de referência carregada! O personagem será mantido em todas as cenas.', 'success');
    };
    reader.readAsDataURL(file);
}

function useAsReferenceModal() {
    if (!FlowState.currentModalResult) return;
    // Usa a imagem do resultado como referência global
    FlowState.referenceImage = FlowState.currentModalResult.url;
    document.getElementById('ref-preview').src = FlowState.referenceImage;
    document.getElementById('ref-preview').style.display = 'block';
    document.getElementById('ref-placeholder').style.display = 'none';
    closeModal();
    showToast('✅ Imagem definida como referência de personagem!', 'success');
}

// =========================================
// GERENCIADOR DE CENAS
// =========================================
let sceneCounter = 0;

function addScene() {
    sceneCounter++;
    const sceneId = `scene_${sceneCounter}`;
    const engineOptions = Object.entries(ENGINE_LABELS)
        .map(([val, label]) => `<option value="${val}">${label} (${ENGINE_COSTS[val]} 💎)</option>`)
        .join('');
    
    const sceneObj = {
        id: sceneId,
        prompt: '',
        engine: 'flux',
        number: sceneCounter
    };
    FlowState.scenes.push(sceneObj);

    const container = document.getElementById('scenes-container');
    const card = document.createElement('div');
    card.className = 'scene-card';
    card.id = sceneId;
    card.innerHTML = `
        <div class="scene-card-header">
            <div class="scene-number">${sceneCounter}</div>
            <div class="scene-label">Cena ${sceneCounter}</div>
            <span class="scene-engine-badge engine-badge flux" id="badge_${sceneId}">⚡ Flux</span>
            <button class="scene-remove-btn" onclick="removeScene('${sceneId}')"><i class="fas fa-times"></i></button>
        </div>
        <div class="scene-card-body">
            <textarea class="scene-prompt-input" 
                id="prompt_${sceneId}"
                placeholder="Descreva a Cena ${sceneCounter}... Ex: 'Câmera wide shot de uma cidade futurista ao pôr do sol'" 
                oninput="updateScenePrompt('${sceneId}', this.value)"></textarea>
            <select class="scene-engine-select" id="engine_${sceneId}" onchange="updateSceneEngine('${sceneId}', this.value)">
                ${engineOptions}
            </select>
        </div>
    `;
    container.appendChild(card);

    // Animação de entrada
    setTimeout(() => card.style.opacity = '1', 10);
    updateIgniteCost();
}

function removeScene(sceneId) {
    if (FlowState.scenes.length <= 1) {
        showToast('⚠️ O Flow precisa de pelo menos uma cena!', 'error');
        return;
    }
    FlowState.scenes = FlowState.scenes.filter(s => s.id !== sceneId);
    document.getElementById(sceneId)?.remove();
    updateIgniteCost();
}

function updateScenePrompt(sceneId, value) {
    const scene = FlowState.scenes.find(s => s.id === sceneId);
    if (scene) scene.prompt = value;
}

function updateSceneEngine(sceneId, value) {
    const scene = FlowState.scenes.find(s => s.id === sceneId);
    if (scene) scene.engine = value;
    
    // Atualiza o badge
    const badge = document.getElementById(`badge_${sceneId}`);
    if (badge) {
        badge.className = `scene-engine-badge engine-badge ${value.split('-')[0]}`;
        badge.textContent = ENGINE_LABELS[value] || value;
    }
    updateIgniteCost();
}

function updateIgniteCost() {
    let total = 0;
    FlowState.scenes.forEach(scene => {
        total += (ENGINE_COSTS[scene.engine] || 1) * FlowState.variations;
    });
    const label = document.getElementById('ignite-cost-label');
    if (label) label.textContent = `Custo: ${total} Cristal${total !== 1 ? 'is' : ''}`;
}

// =========================================
// VARIAÇÕES
// =========================================
function changeVariations(delta) {
    FlowState.variations = Math.max(1, Math.min(8, FlowState.variations + delta));
    document.getElementById('variations-val').textContent = FlowState.variations;
    updateIgniteCost();
}

// =========================================
// ESTILO GLOBAL
// =========================================
function toggleStyle(chip) {
    document.querySelectorAll('.style-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    FlowState.activeStyle = chip.textContent;
}

// =========================================
// IGNITE FLOW (Lote)
// =========================================
async function igniteFlow() {
    const btn = document.getElementById('ignite-btn');
    
    // Validação
    const hasEmptyPrompts = FlowState.scenes.some(s => !s.prompt.trim());
    if (hasEmptyPrompts) {
        showToast('⚠️ Preencha o prompt de todas as cenas antes de Ignitar!', 'error');
        return;
    }

    btn.classList.add('loading');
    btn.disabled = true;

    // Limpa empty state
    const grid = document.getElementById('results-grid');
    document.getElementById('empty-state')?.remove();
    document.getElementById('save-all-btn').disabled = false;
    
    setGalleryStatus('running', `🔥 Gerando ${FlowState.scenes.length * FlowState.variations} mídias em lote...`);

    // Dispara gerações por cena e variação
    for (let si = 0; si < FlowState.scenes.length; si++) {
        const scene = FlowState.scenes[si];
        
        for (let vi = 0; vi < FlowState.variations; vi++) {
            const cardId = `result_${scene.id}_v${vi}`;
            const promptWithStyle = `${scene.prompt}, estilo ${FlowState.activeStyle}`;
            
            // Cria card de loading na grade
            createLoadingCard(grid, cardId, scene, si + 1, vi + 1);
            
            // Dispara a geração (não bloqueante)
            dispatchGenerationJob(cardId, promptWithStyle, scene.engine, si + 1, vi + 1);
        }
    }

    setTimeout(() => {
        btn.classList.remove('loading');
        btn.disabled = false;
    }, 1500);
}

async function dispatchGenerationJob(cardId, prompt, engine, sceneNum, varNum) {
    try {
        // Chama nosso Maestro backend de forma assíncrona
        let jobId = null;
        try {
            const response = await fetch(`${MAESTRO_URL}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: 'user_demo',
                    model: engine,
                    prompt: prompt,
                    cost_in_crystals: ENGINE_COSTS[engine] || 1
                })
            });
            if (response.ok) {
                const data = await response.json();
                jobId = data.job_id;
            }
        } catch (e) {
            // Backend não disponível localmente: usa simulação
            console.warn('[FlowLogic] Maestro offline — usando simulação de IA.');
        }

        if (jobId) {
            // Polling real no Maestro
            await pollJobUntilDone(cardId, jobId, sceneNum, varNum, engine, prompt);
        } else {
            // Simulação visual (para desenvolvimento offline)
            await simulateGeneration(cardId, engine, sceneNum, varNum, prompt);
        }

    } catch (err) {
        updateCardError(cardId, `Erro: ${err.message}`);
    }
}

async function pollJobUntilDone(cardId, jobId, sceneNum, varNum, engine, prompt) {
    let attempts = 0;
    const maxAttempts = 60; // 3 minutos (60 * 3s)

    return new Promise((resolve) => {
        const interval = setInterval(async () => {
            attempts++;
            try {
                const res = await fetch(`${MAESTRO_URL}/status/${jobId}`);
                const data = await res.json();
                
                if (data.status === 'completed') {
                    clearInterval(interval);
                    const mediaUrl = data.result?.file_url || data.result?.image_base64 || null;
                    completeCard(cardId, mediaUrl, engine, sceneNum, varNum, prompt);
                    resolve();
                } else if (data.status === 'failed') {
                    clearInterval(interval);
                    updateCardError(cardId, 'Falha na geração — cristal reembolsado');
                    resolve();
                }
            } catch(e) {
                if (attempts >= maxAttempts) {
                    clearInterval(interval);
                    updateCardError(cardId, 'Timeout — cristal reembolsado');
                    resolve();
                }
            }
        }, 3000);
    });
}

// Simulação offline para desenvolvimento
async function simulateGeneration(cardId, engine, sceneNum, varNum, prompt) {
    const delay = 1500 + Math.random() * 3000;
    await new Promise(r => setTimeout(r, delay));
    
    // Usa placeholder de imagem pública
    const mockImages = [
        'https://picsum.photos/seed/' + cardId + '/800/600',
        'https://picsum.photos/seed/' + cardId + 'a/600/800',
        'https://picsum.photos/seed/' + cardId + 'b/1024/576',
    ];
    const url = mockImages[Math.floor(Math.random() * mockImages.length)];
    completeCard(cardId, url, engine, sceneNum, varNum, prompt);
}

// =========================================
// MANIPULAÇÃO DOS CARDS
// =========================================
function createLoadingCard(grid, cardId, scene, sceneNum, varNum) {
    const currentView = grid.classList.contains('storyboard-view') ? 'storyboard' : 'masonry';
    
    const card = document.createElement('div');
    card.className = 'result-card';
    card.id = cardId;
    card.innerHTML = `
        <div class="result-card-scene-tag">Cena ${sceneNum} • #${varNum}</div>
        <div class="result-card-loading">
            <div class="loading-ring"></div>
            <span>${ENGINE_LABELS[scene.engine] || scene.engine}</span>
            <small>Gerando...</small>
        </div>
    `;
    grid.appendChild(card);
}

function completeCard(cardId, mediaUrl, engine, sceneNum, varNum, prompt) {
    const card = document.getElementById(cardId);
    if (!card) return;

    const result = { id: cardId, url: mediaUrl, engine, sceneNum, varNum, prompt };
    FlowState.results.push(result);

    const engineLabel = ENGINE_LABELS[engine] || engine;
    const engineClass = engine.split('-')[0];
    const isVideo = ['hailuo', 'ltx', 'wan', 'kling'].includes(engine.split('-')[0]);
    
    const mediaTag = mediaUrl
        ? (isVideo
            ? `<video src="${mediaUrl}" loop muted autoplay style="width:100%;display:block;"></video>`
            : `<img src="${mediaUrl}" alt="Cena ${sceneNum} Var ${varNum}" loading="lazy">`)
        : `<div style="min-height:200px;display:flex;align-items:center;justify-content:center;color:#64748b;">Sem preview</div>`;

    card.innerHTML = `
        <div class="result-card-scene-tag">Cena ${sceneNum} • #${varNum}</div>
        <div class="card-selection-box" onclick="toggleCardSelection(event, '${cardId}')">
            <i class="fas fa-check"></i>
        </div>
        ${mediaTag}
        <div class="result-card-overlay">
            <span class="result-card-engine engine-badge ${engineClass}">${engineLabel}</span>
            <div class="result-card-actions">
                <button class="result-card-action" title="Garagem" onclick="event.stopPropagation(); saveToGarage('${cardId}')"><i class="fas fa-warehouse"></i></button>
                <button class="result-card-action" title="Editor" onclick="event.stopPropagation(); sendToEditor('${cardId}')"><i class="fas fa-film"></i></button>
                <button class="result-card-action" title="Download" onclick="event.stopPropagation(); downloadResult('${cardId}')"><i class="fas fa-download"></i></button>
            </div>
        </div>
    `;

    // Abre o modal ao clicar na card
    card.onclick = () => openModal(result);

    // Checa se todas as gerações terminaram
    checkAllDone();
}

function updateCardError(cardId, message) {
    const card = document.getElementById(cardId);
    if (!card) return;
    card.innerHTML = `
        <div class="result-card-loading" style="border: 1px dashed rgba(248,113,113,0.4);">
            <i class="fas fa-exclamation-triangle" style="color: #f87171; font-size:24px;"></i>
            <span style="color:#f87171;">Erro na Geração</span>
            <small>${message}</small>
        </div>
    `;
}

function checkAllDone() {
    const loadingCards = document.querySelectorAll('.result-card-loading');
    if (loadingCards.length === 0) {
        const total = FlowState.results.length;
        setGalleryStatus('done', `✅ ${total} mídia${total !== 1 ? 's' : ''} gerada${total !== 1 ? 's' : ''} com sucesso!`);
        showToast(`✅ ${total} gerações concluídas! Confira a galeria.`, 'success');
    }
}

function setGalleryStatus(type, text) {
    const el = document.getElementById('gallery-status');
    if (!el) return;
    el.innerHTML = `<span class="status-${type}">${text}</span>`;
}

// =========================================
// VIEW TOGGLE (Masonry / Storyboard)
// =========================================
function setView(view) {
    const grid = document.getElementById('results-grid');
    document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`view-${view}`).classList.add('active');
    
    if (view === 'masonry') {
        grid.className = 'results-grid masonry-view';
    } else {
        grid.className = 'results-grid storyboard-view';
        reorganizeStoryboard();
    }
}

function reorganizeStoryboard() {
    const grid = document.getElementById('results-grid');
    // Agrupa por cena no modo Storyboard
    const grouped = {};
    FlowState.results.forEach(r => {
        if (!grouped[r.sceneNum]) grouped[r.sceneNum] = [];
        grouped[r.sceneNum].push(r);
    });

    grid.innerHTML = '';
    Object.entries(grouped).forEach(([sceneNum, results]) => {
        const group = document.createElement('div');
        group.className = 'storyboard-scene-group';
        group.innerHTML = `
            <div class="storyboard-scene-label">Cena ${sceneNum}</div>
            <div class="storyboard-cards-row" id="storyboard-row-${sceneNum}"></div>
        `;
        grid.appendChild(group);
        
        results.forEach(r => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.innerHTML = `<img src="${r.url}" alt="Cena ${r.sceneNum}" style="width:100%;display:block;">`;
            card.onclick = () => openModal(r);
            document.getElementById(`storyboard-row-${sceneNum}`).appendChild(card);
        });
    });
}

// =========================================
// GALERIA: Ações
// =========================================
function saveAllToGarage() {
    showToast(`📦 ${FlowState.results.length} mídias enviadas para a Garagem!`, 'success');
}

function clearGallery() {
    FlowState.results = [];
    const grid = document.getElementById('results-grid');
    grid.innerHTML = `
        <div class="empty-state" id="empty-state">
            <div class="empty-icon"><i class="fas fa-wand-magic-sparkles"></i></div>
            <h2>Seu Estúdio Aguarda</h2>
            <p>Configure as cenas na esquerda e pressione <strong>Ignite Flow</strong> para começar.</p>
            <div class="supported-engines">
                <span class="engine-badge flux">⚡ Flux</span>
                <span class="engine-badge hailuo">🌊 Hailuo</span>
                <span class="engine-badge ltx">🎬 LTX-Video</span>
                <span class="engine-badge wan">🔥 WAN2.2</span>
                <span class="engine-badge kling">✨ Kling</span>
            </div>
        </div>
    `;
    document.getElementById('save-all-btn').disabled = true;
    setGalleryStatus('idle', 'Pronto para gerar');
}

function saveToGarage(cardId) {
    showToast('📦 Salvo na Garagem!', 'success');
}

function sendToEditor(cardId) {
    showToast('🎬 Enviado para o Editor!', 'success');
}

function downloadResult(cardId) {
    const result = FlowState.results.find(r => r.id === cardId);
    if (result?.url) {
        const a = document.createElement('a');
        a.href = result.url;
        a.download = `apollo_${cardId}.png`;
        a.target = '_blank';
        a.click();
    }
}

// =========================================
// MODAL (Lightbox)
// =========================================
function openModal(result) {
    FlowState.currentModalResult = result;
    
    const modal = document.getElementById('result-modal');
    document.getElementById('modal-title').textContent = `Cena ${result.sceneNum} — Variação ${result.varNum}`;
    document.getElementById('modal-engine-tag').textContent = ENGINE_LABELS[result.engine] || result.engine;
    document.getElementById('modal-type-tag').textContent = ['ltx','wan','hailuo','kling'].includes(result.engine) ? 'Vídeo' : 'Imagem';
    document.getElementById('modal-prompt-text').textContent = result.prompt || 'Sem prompt';
    
    const img = document.getElementById('modal-img');
    const video = document.getElementById('modal-video');
    
    if (['ltx','wan','hailuo','kling'].includes(result.engine)) {
        img.style.display = 'none';
        video.src = result.url || '';
        video.style.display = 'block';
    } else {
        video.style.display = 'none';
        img.src = result.url || '';
        img.style.display = 'block';
    }
    
    modal.classList.add('open');
}

function closeModal() {
    document.getElementById('result-modal').classList.remove('open');
    FlowState.currentModalResult = null;
}

function saveToGarageModal() { saveToGarage(FlowState.currentModalResult?.id); closeModal(); }
function sendToEditorModal() { sendToEditor(FlowState.currentModalResult?.id); closeModal(); }
function downloadModal() { downloadResult(FlowState.currentModalResult?.id); }
function upscaleResult(factor) { showToast(`🔍 Upscale ${factor}× iniciado! Chega em breve na Garagem.`, 'success'); }

// =========================================
// MODO: GERAÇÃO RÁPIDA
// =========================================
function selectQuickEngine(card) {
    document.querySelectorAll('#qg-engines .engine-card').forEach(c => c.classList.remove('active'));
    card.classList.add('active');
    FlowState.quickEngine = card.dataset.engine;
    
    const cost = ENGINE_COSTS[FlowState.quickEngine] || 1;
    document.getElementById('qg-cost-label').textContent = `${cost} Cristal${cost !== 1 ? 'is' : ''}`;
    
    // Mostra/oculta opção Img2Vid para motores de vídeo
    const isVideo = ['hailuo','ltx','wan','kling'].includes(FlowState.quickEngine);
    document.getElementById('img2vid-toggle').parentElement.parentElement.style.display = isVideo ? 'flex' : 'none';
}

function toggleImg2Vid() {
    const active = document.getElementById('img2vid-toggle').checked;
    document.getElementById('img2vid-zone').style.display = active ? 'block' : 'none';
}

async function quickGenerate() {
    const prompt = document.getElementById('qg-prompt').value.trim();
    if (!prompt) {
        showToast('⚠️ Escreva um prompt antes de gerar!', 'error');
        return;
    }

    const btn = document.getElementById('qg-generate-btn');
    btn.disabled = true;
    btn.innerHTML = '<div class="loading-ring" style="width:20px;height:20px;border-width:2px;"></div> Gerando...';

    const resultPanel = document.getElementById('qg-result-panel');
    document.getElementById('qg-placeholder').style.display = 'flex';
    document.getElementById('qg-result-content').style.display = 'none';
    
    // Simula geração
    await simulateGeneration('qg-current', FlowState.quickEngine, 1, 1, prompt);
    
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-sparkles"></i> <span>Gerar Novamente</span><small>' + (ENGINE_COSTS[FlowState.quickEngine] || 1) + ' Cristal</small>';

    // Mock de resultado
    const mockUrl = `https://picsum.photos/seed/${Date.now()}/800/600`;
    document.getElementById('qg-placeholder').style.display = 'none';
    document.getElementById('qg-result-content').style.display = 'flex';
    document.getElementById('qg-result-img').src = mockUrl;
    document.getElementById('qg-result-img').style.display = 'block';
    document.getElementById('qg-meta-engine').textContent = ENGINE_LABELS[FlowState.quickEngine];
    document.getElementById('qg-meta-time').textContent = `${(1.5 + Math.random() * 3).toFixed(1)}s`;
    document.getElementById('qg-meta-seed').textContent = `Seed: ${Math.floor(Math.random() * 9999999)}`;
}

function enhancePrompt() {
    const textarea = document.getElementById('qg-prompt');
    const original = textarea.value.trim();
    if (!original) { showToast('⚠️ Escreva algo primeiro para melhorar!', 'error'); return; }
    
    // Simulação de melhoria de prompt por IA
    const additions = [
        ', cinematographic lighting, golden hour, bokeh background',
        ', 8K ultra-detailed, hyperrealistic, professional photography',
        ', dramatic shadows, neon reflections, atmospheric fog',
        ', stunning composition, depth of field, award-winning photo'
    ];
    const enhanced = original + additions[Math.floor(Math.random() * additions.length)];
    textarea.value = enhanced;
    showToast('✨ Prompt melhorado pela I.A.!', 'success');
}

function generateVariations() {
    showToast('🔄 Gerando 4 variações... Confira o Estúdio em Lote!', 'success');
    switchMode('studio');
}

// =========================================
// PRESETS
// =========================================
function savePreset() {
    const preset = {
        scenes: FlowState.scenes.map(s => ({ prompt: s.prompt, engine: s.engine })),
        variations: FlowState.variations,
        style: FlowState.activeStyle
    };
    localStorage.setItem('apollo_flow_preset', JSON.stringify(preset));
    showToast('💾 Preset salvo localmente!', 'success');
}

function loadPreset() {
    const data = localStorage.getItem('apollo_flow_preset');
    if (!data) { showToast('⚠️ Nenhum preset salvo!', 'error'); return; }
    
    try {
        const preset = JSON.parse(data);
        FlowState.scenes = [];
        document.getElementById('scenes-container').innerHTML = '';
        sceneCounter = 0;
        
        preset.scenes.forEach(s => {
            addScene();
            const lastScene = FlowState.scenes[FlowState.scenes.length - 1];
            document.getElementById(`prompt_${lastScene.id}`).value = s.prompt;
            document.getElementById(`engine_${lastScene.id}`).value = s.engine;
            updateSceneEngine(lastScene.id, s.engine);
            updateScenePrompt(lastScene.id, s.prompt);
        });
        
        FlowState.variations = preset.variations || 2;
        document.getElementById('variations-val').textContent = FlowState.variations;
        updateIgniteCost();
        showToast('📂 Preset carregado com sucesso!', 'success');
    } catch(e) {
        showToast('❌ Erro ao carregar preset!', 'error');
    }
}

// =========================================
// SELEÇÃO MÚLTIPLA NA GALERIA
// =========================================
function toggleCardSelection(event, cardId) {
    // Evita abrir o modal se clicar no checkbox
    event.stopPropagation();
    const card = document.getElementById(cardId);
    if (!card) return;
    
    card.classList.toggle('selected');
    updateSelectionBar();
}

function updateSelectionBar() {
    const selected = document.querySelectorAll('.result-card.selected');
    const bar = document.getElementById('gallery-selection-bar');
    const count = document.getElementById('sel-count');
    
    if (selected.length > 0) {
        count.textContent = selected.length;
        bar.classList.add('visible');
    } else {
        bar.classList.remove('visible');
    }
}

function clearSelection() {
    document.querySelectorAll('.result-card.selected').forEach(c => c.classList.remove('selected'));
    updateSelectionBar();
}

function saveSelectedToGarage() {
    const selected = document.querySelectorAll('.result-card.selected');
    showToast(`📦 ${selected.length} mídias enviadas para a Garagem!`, 'success');
    clearSelection();
}

function sendSelectedToEditor() {
    const selected = document.querySelectorAll('.result-card.selected');
    showToast(`🎬 ${selected.length} mídias enviadas para o Editor!`, 'success');
    clearSelection();
}

function deleteSelected() {
    const selected = document.querySelectorAll('.result-card.selected');
    selected.forEach(c => {
        FlowState.results = FlowState.results.filter(r => r.id !== c.id);
        c.remove();
    });
    showToast(`🗑️ ${selected.length} mídias excluídas.`, 'success');
    clearSelection();
    if (FlowState.results.length === 0) clearGallery();
}

// =========================================
// TOAST
// =========================================
function showToast(message, type = 'default') {
    const toast = document.getElementById('flow-toast');
    toast.textContent = message;
    toast.className = `flow-toast show ${type}`;
    setTimeout(() => { toast.classList.remove('show'); }, 4000);
}

// Fechar modal com ESC
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
});
