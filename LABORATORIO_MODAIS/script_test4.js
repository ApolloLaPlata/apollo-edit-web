
// ─── ESTADO GLOBAL ──────────────────────────────────────────────────────────
let currentImageData = null;
let currentVideoData = null;
let timerInterval = null;
let startTime = null;

// ─── UTILIDADES ─────────────────────────────────────────────────────────────
function ts() { return new Date().toLocaleTimeString('pt-BR', {hour12:false}); }

function log(msg, type='info') {
    const tb = document.getElementById('terminalBody');
    const cls = type === 'error' ? 'log-err' : type === 'ok' ? 'log-ok' : type === 'warn' ? 'log-warn' : 'log-info';
    tb.innerHTML += `\n<span class="log-time">[${ts()}]</span> <span class="${cls}">${msg}</span>`;
    tb.scrollTop = tb.scrollHeight;
}

function getBaseUrl() {
    return document.getElementById('modalUrl').value.trim().replace(/\/$/, '');
}

function b64toBlob(b64, mime) {
    const bytes = atob(b64);
    const arr = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
    return new Blob([arr], {type: mime});
}

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const m = String(Math.floor(elapsed / 60)).padStart(2,'0');
        const s = String(elapsed % 60).padStart(2,'0');
        document.getElementById('timerDisplay').textContent = `${m}:${s}`;
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    document.getElementById('genTimeBadge').textContent = `⏱️ ${elapsed}s`;
    document.getElementById('genTimeBadge').style.display = 'inline-block';
    return elapsed;
}

function showSpinner(label) {
    document.getElementById('previewPlaceholder').style.display = 'none';
    document.getElementById('previewImage').style.display = 'none';
    document.getElementById('previewVideo').style.display = 'none';
    document.getElementById('spinnerWrap').classList.add('active');
    document.getElementById('spinnerLabel').textContent = label;
    document.getElementById('timerDisplay').textContent = '00:00';
    startTimer();
}

function hideSpinner() {
    document.getElementById('spinnerWrap').classList.remove('active');
}

function clearPreview() {
    const imgNode = document.getElementById('previewImage');
    imgNode.style.display = 'none';
    imgNode.src = '';

    const vidNode = document.getElementById('previewVideo');
    vidNode.style.display = 'none';
    vidNode.src = '';
    
    document.getElementById('btnDownloadPreview').style.display = 'none';
    document.getElementById('spinnerWrap').classList.remove('active');
    document.getElementById('previewPlaceholder').style.display = 'flex';
    document.getElementById('genTimeBadge').style.display = 'none';
    currentImageData = null;
    currentVideoData = null;
}

        // --- GESTÃO DE ABAS ---
        function showTab(name) {
            ['img', 'vid', 'audio', 'music', 'batch'].forEach(t => {
                const el = document.getElementById('tab-'+t);
                if (el) el.style.display = (t === name) ? 'block' : 'none';
            });
            
            document.querySelectorAll('.tab-btn').forEach((b,i) => {
                const tabs = ['img','vid','audio','music', 'batch'];
                if (tabs[i]) b.classList.toggle('active', tabs[i] === name);
            });
        }


function copyLogs() {
    const text = document.getElementById('terminalBody').innerText;
    navigator.clipboard.writeText(text).then(() => {
        log('✅ Logs copiados para a área de transferência!', 'ok');
    });
}

function copyTranscription() {
    const text = document.getElementById('transcriptionResult').innerText;
    navigator.clipboard.writeText(text).then(() => log('✅ Transcrição copiada!', 'ok'));
}

function downloadImage() {
    if (!currentImageData) return;
    const a = document.createElement('a');
    a.href = 'data:image/png;base64,' + currentImageData;
    a.download = `apollo_flux_${Date.now()}.png`;
    a.click();
    log('💾 Download da imagem iniciado.', 'ok');
}

function downloadVideo() {
    if (!currentVideoData) return;
    const blob = b64toBlob(currentVideoData, 'video/mp4');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `apollo_ltx_${Date.now()}.mp4`;
    a.click();
    log('💾 Download do vídeo iniciado.', 'ok');
}

function downloadCurrentMedia() {
    if (currentImageData) {
        downloadImage();
    } else if (currentVideoData) {
        downloadVideo();
    }
}

function updateFileName() {
    const file = document.getElementById('audioFile').files[0];
    document.getElementById('audioFileName').textContent = file ? file.name : 'Nenhum arquivo selecionado';
}

function updateImgRefNames() {
    const files = document.getElementById('imgRefFiles').files;
    const label = document.getElementById('imgRefFileNames');
    if (files.length === 0) {
        label.textContent = 'Nenhuma imagem selecionada';
    } else if (files.length === 1) {
        label.textContent = files[0].name;
    } else {
        label.textContent = `${files.length} imagens selecionadas`;
    }
    updateGenButtonState();
}

function updateGenButtonState() {
    const files = document.getElementById('imgRefFiles').files;
    const model = document.getElementById('imgModel').value;
    const btn = document.getElementById('btnGenImg');
    
    if (files.length >= 2 && model === 'qwen-image') {
        btn.innerHTML = '✨ Gerar Cena Multi-Pass (LLM Text-Locking Ativado)';
        btn.style.background = 'linear-gradient(90deg, #ff0055, #7000ff)';
    } else {
        btn.innerHTML = '✨ Gerar Imagem';
        btn.style.background = 'var(--primary)';
    }
}

function updateImgBaseName() {
    const file = document.getElementById('imgBaseFile').files[0];
    document.getElementById('imgBaseFileName').textContent = file ? file.name : 'Nenhuma imagem selecionada';
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
    });
}

function animateProgress(fillId, textId, startPct, endPct, duration, label) {
    return new Promise(resolve => {
        const fill = document.getElementById(fillId);
        const text = document.getElementById(textId);
        let current = startPct;
        const step = (endPct - startPct) / (duration / 200);
        const iv = setInterval(() => {
            current = Math.min(current + step, endPct);
            fill.style.width = current + '%';
            text.textContent = `${label} — ${Math.round(current)}%`;
            if (current >= endPct) { clearInterval(iv); resolve(); }
        }, 200);
    });
}

// ─── PING ────────────────────────────────────────────────────────
async function pingModal() {
    const url = "/api/studio/modal/ping";
    log(`📡 Ping → ${url}`, 'info');
    
    document.getElementById('latencyBadge').textContent = '...';
    document.getElementById('latencyBadge').className = 'latency-badge';
    
    const t0 = Date.now();
    try {
        const res = await fetch(url, { method: 'GET' });
        const elapsed = Date.now() - t0;
        
        if(res.ok) {
            document.getElementById('latencyBadge').textContent = elapsed + 'ms';
            document.getElementById('latencyBadge').classList.add(elapsed < 2000 ? 'fast' : 'slow');
            log(`✅ Ping OK — ${elapsed}ms`, 'info');
        } else {
            throw new Error(`Status ${res.status}`);
        }
    } catch(err) {
        document.getElementById('latencyBadge').textContent = 'ERRO';
        document.getElementById('latencyBadge').classList.add('slow');
        log(`❌ Erro no Ping: ${err.message}`, 'error');
    }
}

// ─── GERAR IMAGEM ────────────────────────────────────────────────
async function generateImage() {
    const prompt = document.getElementById('promptImg').value.trim();
    const steps  = parseInt(document.getElementById('imgSteps').value) || 28;
    const aspect_ratio = document.getElementById('imgAspect') ? document.getElementById('imgAspect').value : 'horizontal';
    const model = document.getElementById('imgModel') ? document.getElementById('imgModel').value : 'flux-schnell';
    const use_upscale = document.getElementById('toggleUpscale') ? document.getElementById('toggleUpscale').checked : true;
    const url    = "/api/studio/modal/generate_image";
    const status = document.getElementById('imgStatus');

    log(`✨ GERAR IMAGEM — Iniciando`, 'info');
    log(`→ Modelo: ${model} | Formato: ${aspect_ratio} | Upscale: ${use_upscale ? 'ON' : 'OFF'}`, 'info');
    log(`→ Enviando para proxy local: ${url}`, 'info');

    document.getElementById('btnGenImg').disabled = true;
    document.getElementById('imgDownloadBar').classList.remove('visible');
    document.getElementById('imgProgress').style.display = 'block';

    const modelLabels = {
        'flux-schnell': 'Aquecendo L4 • Carregando FLUX.1-schnell...',
        'flux-dev':     'Aquecendo A10G • Carregando FLUX.1-dev...',
        'flux-pulid':   'Aquecendo A10G • Carregando FLUX PuLID...',
        'flux-translated': 'Aquecendo A10G • Preparando Workflow Img2Img...',
        'qwen-image': 'Aquecendo GPU (H100) ⚡ Carregando Qwen Image Edit Plus...'
    };
    showSpinner(modelLabels[model] || 'Aquecendo GPU...');

    try {
        const files = document.getElementById('imgRefFiles').files;
        let reference_images_base64 = null;

        if (files && files.length > 0) {
            reference_images_base64 = [];
            for (let i = 0; i < files.length; i++) {
                const b64 = await fileToBase64(files[i]);
                reference_images_base64.push(b64);
            }
            log(`📸 Anexando ${files.length} imagem(ns) de referência`, 'info');
        }

        if (model === 'flux-translated' && (!reference_images_base64 || reference_images_base64.length === 0)) {
            throw new Error('O modelo Img2Img (flux-translated) EXIGE uma imagem de referência. Selecione uma imagem antes de gerar.');
        }

        animateProgress('imgProgressFill','imgProgressText', 0, 30, 8000, 'Aguardando Modal Cloud');
        log(`⏳ Requisição enviada — aguardando resposta da Modal (pode levar 1-4 min no cold start)...`, 'warn');

        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, steps, aspect_ratio, model, reference_images_base64, use_upscale })
        });

        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`HTTP ${res.status}: ${errText}`);
        }

        const initialData = await res.json();
        if (initialData.status === "processing" && initialData.job_id) {
            const jobId = initialData.job_id;
            log(`📦 Job enfileirado no backend (ID: ${jobId.substring(0,6)}...). Iniciando polling...`, 'info');
            
            let jobSuccess = false;
            let jobData = null;
            while (!jobSuccess) {
                await new Promise(resolve => setTimeout(resolve, 5000));
                
                const now = Math.floor((Date.now() - startTime)/1000);
                log(`💓 Consultando status... (${now}s)`, 'info');
                document.getElementById('spinnerLabel').textContent = `Gerando na Nuvem... ${now}s`;
                
                const statusRes = await fetch(`/api/studio/modal/status/${jobId}`);
                if (!statusRes.ok) {
                    throw new Error(`Erro ao consultar status: HTTP ${statusRes.status}`);
                }
                const statusData = await statusRes.json();
                
                if (statusData.status === "success") {
                      jobSuccess = true;
                      if (typeof statusData.content === 'string') {
                          const lines = statusData.content.trim().split('\n');
                          for (let i = lines.length - 1; i >= 0; i--) {
                              if (lines[i].trim() === "") continue;
                              try {
                                  const parsed = JSON.parse(lines[i]);
                                  if (parsed.image_base64) {
                                      jobData = parsed;
                                      break; // Pega a última que tenha imagem (que será o upscale)
                                  } else if (!jobData) {
                                      jobData = parsed;
                                  }
                              } catch(e) {}
                          }
                          if (!jobData) jobData = statusData.content;
                      } else {
                          jobData = statusData.content;
                      }
                  } else if (statusData.status === "error") {
                      throw new Error(`Erro gerando na Modal: ${JSON.stringify(statusData.content)}`);
                  }
            }
            
            const data = jobData;
            if (data.type === "result" || data.status === "success" || data.image_base64) {
                log(`📦 Recebimento de imagem concluído.`, 'ok');
                const elapsedSec = stopTimer();
                animateProgress('imgProgressFill','imgProgressText', 30, 100, 500, 'Concluído');
                hideSpinner();
                
                currentImageData = data.image_base64 || data.audio_base64 || data.video_url || "";
                document.getElementById('imgSavePath').textContent = data.file_saved || "Base64 recebido";
                
                const imgNode = document.getElementById('previewImage');
                imgNode.src = 'data:image/png;base64,' + currentImageData;
                imgNode.style.display = 'block';
                document.getElementById('imgDownloadBar').classList.add('visible');
                document.getElementById('btnDownloadPreview').style.display = 'block';
                
                status.textContent = `✅ Imagem gerada em ${elapsedSec}s!`;
                log(`✨ IMAGEM GERADA COM SUCESSO! (${elapsedSec}s)`, 'ok');
            } else if (data && (data.status === "error" || data.error || data.message)) {
                throw new Error("Erro da Modal: " + (data.message || data.error || JSON.stringify(data, null, 2)));
            } else {
                throw new Error("Formato de resposta inesperado: " + JSON.stringify(data, null, 2));
            }
        } else {
            throw new Error("O servidor não retornou um Job ID: " + JSON.stringify(initialData, null, 2));
        }

    } catch(e) {
        stopTimer();
        hideSpinner();
        status.textContent = `❌ ERRO: ${e.message}`;
        log(`❌ FALHA: ${e.message}`, 'error');
        log(`→ Dica: Copie os logs acima e cole no chat para análise.`, 'warn');
    } finally {
        document.getElementById('btnGenImg').disabled = false;
        document.getElementById('imgProgress').style.display = 'none';
    }
}

// ─── GERAR VÍDEO ─────────────────────────────────────────────────
async function generateVideo() {
    const prompt = document.getElementById('promptVid').value.trim();
    const model  = document.getElementById('vidModel').value;
    const preset = document.getElementById('vidPreset').value;
    const aspect_ratio = document.getElementById('vidAspect') ? document.getElementById('vidAspect').value : 'horizontal';
    const duration_el = document.getElementById('vidDuration');
    const duration = duration_el ? duration_el.value : '5s';
    const url    = "/api/studio/modal/generate_video";
    const status = document.getElementById('vidStatus');

    log(`🎬 GERAR VÍDEO — Iniciando`, 'info');
    log(`→ Roteando via Backend: ${url}`, 'info');

    document.getElementById('btnGenVid').disabled = true;
    document.getElementById('vidDownloadBar').classList.remove('visible');
    document.getElementById('vidProgress').style.display = 'block';
    showSpinner(`Renderizando vídeo • ${model.toUpperCase()}...`);

    try {
        let imageBase64 = null;
        const imgFile = document.getElementById('imgBaseFile').files[0];
        if (imgFile) {
            log(`→ Processando imagem base: ${imgFile.name}`, 'info');
            imageBase64 = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.readAsDataURL(imgFile);
                reader.onload  = () => resolve(reader.result.split(',')[1]);
                reader.onerror = reject;
            });
            log(`→ Imagem convertida para base64 (${imageBase64.length} chars)`, 'info');
        }

        animateProgress('vidProgressFill','vidProgressText', 0, 20, 15000, 'Calculando Tensores');
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, image_base64: imageBase64, model, preset, aspect_ratio, duration })
        });
        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`HTTP ${res.status}: ${errText}`);
        }

        const initialData = await res.json();
        let data = null;

        if (initialData.status === 'processing' && initialData.job_id) {
            const jobId = initialData.job_id;
            log(`📦 Job enfileirado no backend (ID: ${jobId}). Iniciando polling...`, 'info');
            
            let jobSuccess = false;
            while (!jobSuccess) {
                await new Promise(resolve => setTimeout(resolve, 5000));
                
                const now = Math.floor((Date.now() - startTime)/1000);
                log(`💓 Consultando status... (${now}s)`, 'info');
                document.getElementById('spinnerLabel').textContent = `Gerando Vídeo... ${now}s`;
                
                const statusRes = await fetch(`/api/studio/modal/status/${jobId}`);
                if (!statusRes.ok) {
                    throw new Error(`Erro ao consultar status: HTTP ${statusRes.status}`);
                }
                const statusData = await statusRes.json();
                
                if (statusData.status === 'success') {
                    jobSuccess = true;
                    if (typeof statusData.content === 'string') {
                        data = JSON.parse(statusData.content);
                    } else {
                        data = statusData.content;
                    }
                } else if (statusData.status === 'error') {
                    throw new Error(statusData.message || 'Erro na nuvem ao processar vídeo.');
                }
            }
        } else {
            data = initialData;
        }

        if (data.status === 'success' && data.video_base64) {
            const elapsed = stopTimer();
            animateProgress('vidProgressFill','vidProgressText', 90, 100, 300, 'Concluído');

            currentVideoData = data.video_base64;
            hideSpinner();

            const blob = b64toBlob(data.video_base64, 'video/mp4');
            const vidUrl = URL.createObjectURL(blob);
            const vid = document.getElementById('previewVideo');
            vid.src = vidUrl;
            vid.style.display = 'block';
            document.getElementById('btnDownloadPreview').style.display = 'block';

            status.className = 'log-box';
            status.textContent = `✅ Vídeo renderizado em ${elapsed}s!\nSalvo: ${data.file_saved || 'N/A'}`;

            document.getElementById('vidSavePath').textContent = data.file_saved || '';
            document.getElementById('vidDownloadBar').classList.add('visible');

            log(`✅ VÍDEO GERADO em ${elapsed}s`, 'ok');
        } else {
            throw new Error(data.message || data.detail || JSON.stringify(data));
        }
    } catch(e) {
        const elapsed = stopTimer();
        hideSpinner();
        clearPreview();
        document.getElementById('previewPlaceholder').style.display = 'flex';

        status.className = 'log-box error';
        status.textContent = `❌ ERRO após ${elapsed}s:\n${e.message}`;

        log(`❌ FALHA NO VÍDEO após ${elapsed}s: ${e.message}`, 'error');
    } finally {
        document.getElementById('btnGenVid').disabled = false;
        document.getElementById('vidProgress').style.display = 'none';
    }
}

// ─── TRANSCREVER ÁUDIO ───────────────────────────────────────────────────────
async function transcribeAudio() {
    const file = document.getElementById('audioFile').files[0];
    if (!file) { alert('Selecione um arquivo de áudio!'); return; }

    const status = document.getElementById('audioStatus');
    const result = document.getElementById('transcriptionResult');
    const url    = "/api/studio/modal/transcribe";

    log(`🎤 TRANSCRIÇÃO — Iniciando`, 'info');
    log(`→ Arquivo: ${file.name} (${(file.size/1024/1024).toFixed(2)} MB)`, 'info');
    log(`→ Roteando via Backend: ${url}`, 'info');

    document.getElementById('btnTranscribe').disabled = true;
    showSpinner('Transcrevendo com Whisper v3...');
    status.className = 'log-box info';
    status.textContent = '⏳ Codificando áudio em base64...';
    result.innerHTML = '<span style="color:var(--text-dim)">Processando...</span>';

    try {
        // Converter para base64
        const b64 = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload  = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
        });
        log(`→ Áudio codificado: ${b64.length} chars base64`, 'info');

        status.textContent = '⏳ Enviando para Whisper v3 na GPU T4...';

        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audio_base64: b64 })
        });

        const rawText = await res.text();
        let data;
        try { 
            const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0 && l.startsWith('{'));
            if (lines.length > 0) {
                data = JSON.parse(lines[lines.length - 1]);
            } else {
                throw new Error("Nenhum JSON encontrado");
            }
        }
        catch(pe) {
            throw new Error('Resposta inválida do servidor.');
        }

        if (data.status === 'success') {
            const elapsed = stopTimer();
            hideSpinner();
            status.className = 'log-box';
            status.textContent = `✅ Transcrição concluída em ${elapsed}s!`;
            result.textContent = data.text;
            log(`✅ TRANSCRIÇÃO OK em ${elapsed}s — ${data.text.length} chars`, 'ok');
        } else {
            throw new Error(data.message || JSON.stringify(data));
        }
    } catch(e) {
        const elapsed = stopTimer();
        hideSpinner();
        status.className = 'log-box error';
        status.textContent = `❌ ERRO: ${e.message}`;
        result.innerHTML = '<span style="color:var(--red)">Falha na transcrição.</span>';
        log(`❌ TRANSCRIÇÃO FALHOU após ${elapsed}s: ${e.message}`, 'error');
    } finally {
        document.getElementById('btnTranscribe').disabled = false;
    }
}

// ─── INICIALIZAÇÃO ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    log('🚀 Apollo Modal AI Studio v2.0 carregado', 'ok');
    log('→ Conectado via proxy seguro no backend.', 'info');
    log('→ Dica: cole os logs abaixo no chat se algo falhar!', 'warn');
    // Auto-ping ao carregar
    setTimeout(pingModal, 1500);

    // ─── Toggle Upscale Visual ─────────────────────────────────────
    const toggleUpscale = document.getElementById('toggleUpscale');
    const toggleSlider  = document.getElementById('toggleUpscaleSlider');
    const upscaleBadge  = document.getElementById('upscaleBadge');

    function applyUpscaleStyle(checked) {
        toggleSlider.style.background = checked ? 'var(--green)' : '#444';
        toggleSlider.style.setProperty('--slider-x', checked ? '18px' : '0px');
        upscaleBadge.textContent = checked ? 'ON' : 'OFF';
        upscaleBadge.style.background = checked ? 'var(--green)' : '#555';
        upscaleBadge.style.color = checked ? '#000' : '#ccc';
    }

    // Pseudo-element não funciona inline, então usamos um pseudo-span interno
    toggleSlider.innerHTML = '<span id="sliderThumb" style="position:absolute; top:2px; left:2px; width:18px; height:18px; background:#fff; border-radius:50%; transition:0.3s;"></span>';

    function applyUpscaleStyleFull(checked) {
        toggleSlider.style.background = checked ? '#00ff88' : '#444';
        document.getElementById('sliderThumb').style.transform = checked ? 'translateX(18px)' : 'translateX(0)';
        upscaleBadge.textContent = checked ? 'ON' : 'OFF';
        upscaleBadge.style.background = checked ? 'var(--green)' : '#555';
        upscaleBadge.style.color = checked ? '#000' : '#ccc';
    }

    applyUpscaleStyleFull(toggleUpscale.checked);
    toggleUpscale.addEventListener('change', () => applyUpscaleStyleFull(toggleUpscale.checked));
});
        // --- BATCH GENERATION LOGIC ---
        let batchRunning = false;
        
        function toggleRandomDuration() {
            const isRandom = document.getElementById('batchRandomDuration').checked;
            document.getElementById('batchDurationFixedContainer').style.display = isRandom ? 'none' : 'block';
            document.getElementById('batchDurationRandomContainer').style.display = isRandom ? 'flex' : 'none';
        }
        
        
        
        function logBatch(msg) {
            const box = document.getElementById('batchStatus');
            box.innerText = msg;
        }
        
        function updateBatchProgress(current, total) {
            const perc = (current / total) * 100;
            document.getElementById('batchProgressBar').style.width = perc + '%';
            document.getElementById('batchProgressText').innerText = `${current}/${total}`;
        }

        
        
        async function autoTagLyrics() {
            const btn = document.getElementById('btnAutoTag');
            const el = document.getElementById('musicSingleLyrics');
            const raw = el.value.trim();
            
            if (!raw) return alert("Digite a letra primeiro para a IA estruturar!");
            
            btn.innerText = "⏳ Pensando...";
            btn.disabled = true;
            
            try {
                const response = await fetch("/api/music/auto_tag_lyrics", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ lyrics: raw })
                });
                const result = await response.json();
                
                if (result.success) {
                    el.value = result.structured_lyrics;
                    btn.innerText = "✅ Aplicado!";
                } else {
                    alert("Erro da IA: " + result.error);
                    btn.innerText = "❌ Falha";
                }
            } catch (e) {
                alert("Erro de rede.");
                btn.innerText = "❌ Erro";
            }
            
            setTimeout(() => {
                btn.innerText = "🪄 Auto-Tag (IA)";
                btn.disabled = false;
            }, 3000);
        }

        async function generateBatchIdeas() {
            const btn = document.getElementById('btnAIGenerateBatch');
            const theme = document.getElementById('aiBatchTheme').value.trim();
            const count = parseInt(document.getElementById('aiBatchCount').value) || 3;
            
            if (!theme) return alert("Digite o tema desejado!");
            
            btn.innerText = "⏳ Gerando...";
            btn.disabled = true;
            
            try {
                const response = await fetch("/api/music/generate_batch_ideas", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ theme, count })
                });
                const result = await response.json();
                
                if (result.success && result.tracks.length > 0) {
                    let promptStr = "";
                    let lyricStr = "";
                    
                    result.tracks.forEach((track, i) => {
                        promptStr += track.style + "\n";
                        lyricStr += track.lyrics + "\n";
                        if (i < result.tracks.length - 1) lyricStr += "\n===\n";
                    });
                    
                    document.getElementById('musicBatchPrompts').value = promptStr.trim();
                    document.getElementById('musicBatchLyrics').value = lyricStr.trim();
                    
                    // Force change to Vocal mode since AI generated lyrics
                    document.getElementById('musicStyle').value = 'vocal';
                    toggleMusicUI();
                    
                    btn.innerText = "✅ Ideias Prontas!";
                } else {
                    alert("Erro da IA: " + (result.error || "Formato inválido retornado."));
                    btn.innerText = "❌ Falha";
                }
            } catch (e) {
                alert("Erro de rede.");
                btn.innerText = "❌ Erro";
            }
            
            setTimeout(() => {
                btn.innerText = "✨ Gerar Ideias";
                btn.disabled = false;
            }, 3000);
        }

        function insertTag(targetId, tag) {
            const el = document.getElementById(targetId);
            const start = el.selectionStart;
            const end = el.selectionEnd;
            const text = el.value;
            el.value = text.substring(0, start) + tag + "\n" + text.substring(end);
            el.focus();
            el.selectionEnd = start + tag.length + 1;
        }

        function magicStyle(targetId) {
            const el = document.getElementById(targetId);
            let val = el.value.trim();
            if (!val) val = "Trap";
            
            // Simple rule-based enhancement
            if (!val.toLowerCase().includes("quality")) val += ", masterpiece, ultra high quality, crisp audio";
            if (!val.toLowerCase().includes("bpm") && val.toLowerCase().includes("trap")) val += ", 140 bpm, heavy 808 bass, fast hi-hats";
            if (val.toLowerCase().includes("rock") && !val.toLowerCase().includes("guitar")) val += ", distorted electric guitars, heavy drums, stadium rock";
            if (val.toLowerCase().includes("lo-fi") || val.toLowerCase().includes("lofi")) val += ", vinyl crackle, cozy, relaxing, melodic piano";
            
            el.value = val;
            
            // Visual feedback
            const btn = event.target;
            const old = btn.innerText;
            btn.innerText = "✅ Aplicado!";
            setTimeout(() => { btn.innerText = old; }, 2000);
        }

        // --- MASTER MUSIC GENERATION LOGIC ---
        let musicRunning = false;
        
        function toggleMusicUI() {
            const execMode = document.querySelector('input[name="musicExecMode"]:checked').value;
            const style = document.getElementById('musicStyle').value;
            const durationMode = document.getElementById('musicDurationMode').value;
            
            // Single vs Batch Areas
            if (execMode === 'single') {
                document.getElementById('musicSingleArea').style.display = 'block';
                document.getElementById('musicBatchArea').style.display = 'none';
                document.getElementById('musicSingleLyricsContainer').style.display = (style === 'vocal') ? 'block' : 'none';
            } else {
                document.getElementById('musicSingleArea').style.display = 'none';
                document.getElementById('musicBatchArea').style.display = 'block';
                document.getElementById('musicBatchLyricsContainer').style.display = (style === 'vocal') ? 'block' : 'none';
            }
            
            // Duration Areas
            document.getElementById('musicDurationFixedArea').style.display = (durationMode === 'fixed') ? 'block' : 'none';
            document.getElementById('musicDurationRandomArea').style.display = (durationMode === 'random') ? 'flex' : 'none';
        }
        
        function stopMusicMaster() {
            musicRunning = false;
            logMusicMaster("Cancelamento solicitado...");
        }
        
        function logMusicMaster(msg) {
            document.getElementById('musicMasterStatus').innerText = msg;
        }
        
        function updateMusicProgress(current, total) {
            const perc = (current / total) * 100;
            document.getElementById('musicProgressBar').style.width = perc + '%';
            document.getElementById('musicProgressText').innerText = current + "/" + total;
        }
        
        
        function downloadAllBatchFiles() {
            if (!window.batchGeneratedFiles || window.batchGeneratedFiles.length === 0) {
                alert("Nenhuma música foi gerada para baixar.");
                return;
            }
            logMusicMaster("Iniciando download em lote...");
            let delay = 0;
            window.batchGeneratedFiles.forEach((url, index) => {
                setTimeout(() => {
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = url.split("/").pop(); // extrai o nome final do arquivo
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    logMusicMaster("Baixando arquivo " + (index + 1) + "...");
                }, delay);
                delay += 800; // 800ms delay para não travar o navegador
            });
        }

        async function generateMusicMaster() {
            const execMode = document.querySelector('input[name="musicExecMode"]:checked').value;
            const style = document.getElementById('musicStyle').value;
            const durationMode = document.getElementById('musicDurationMode').value;
            const engine = document.getElementById('musicModel').value;
            
            let prompts = [];
            let lyrics = [];
            
            // Extract prompts based on mode
            if (execMode === 'single') {
                const singlePrompt = document.getElementById('musicSinglePrompt').value.trim();
                if (!singlePrompt) return alert("Insira o prompt do estilo!");
                prompts.push(singlePrompt);
                
                if (style === 'vocal') {
                    lyrics.push(document.getElementById('musicSingleLyrics').value.trim());
                }
            } else {
                const rawPrompts = document.getElementById('musicBatchPrompts').value.trim();
                if (!rawPrompts) return alert("Insira ao menos um prompt!");
                prompts = rawPrompts.split('\n').map(p => p.trim()).filter(p => p);
                
                if (style === 'vocal') {
                    const rawLyrics = document.getElementById('musicBatchLyrics').value.trim();
                    if (rawLyrics) {
                        lyrics = rawLyrics.split('===').map(l => l.trim()).filter(l => l);
                    }
                    if (lyrics.length > 0 && lyrics.length !== prompts.length) {
                        if (!confirm("Você forneceu " + prompts.length + " estilos e " + lyrics.length + " letras. Continuar?")) return;
                    }
                }
            }
            
            if (prompts.length === 0) return;
            
            document.getElementById('btnGenerateMusicMaster').style.display = 'none';
            document.getElementById('btnStopMusicMaster').style.display = 'block';
            if (prompts.length > 1) document.getElementById('musicProgressContainer').style.display = 'block';
            
            musicRunning = true;
            let successCount = 0;
            
            window.batchGeneratedFiles = [];
            document.getElementById('previewPlaceholder').style.display = 'none';
            const preview = document.getElementById('previewContainer');
            preview.style.display = 'block';
            
            preview.innerHTML = 
                <div style="padding: 20px;">
                    <h2 style="color: white; margin-bottom: 20px; text-align: center;">🚀 Resultados da Sessão</h2>
                    <div id="batchDownloadAllContainer" style="text-align:center; margin-bottom: 20px; display:none;">
                        <button class="btn btn-primary" onclick="downloadAllBatchFiles()" style="font-size: 1.2rem; padding: 15px 30px; font-weight: bold; background: #00d2ff; color: black; border: none; box-shadow: 0 0 15px rgba(0, 210, 255, 0.5);">
                            💾 Baixar Todas as Músicas
                        </button>
                    </div>
                    <div id="batchTracksList" style="display:flex; flex-direction:column; gap:15px;"></div>
                </div>
              ;
            
            for (let i = 0; i < prompts.length; i++) {
                if (!musicRunning) break;
                
                let p = prompts[i];
                if (style === 'instrumental') {
                    p += ", instrumental, no vocals, purely instrumental";
                } else if (style === 'vocal') {
                    p += ", vocals, singing, lyrics, singer";
                    if (lyrics[i]) {
                        p += "\n\nLyrics:\n" + lyrics[i];
                    }
                }
                
                // Duration Calculation
                let finalDuration = 180; // Suno/Auto Default
                if (durationMode === 'fixed') {
                    finalDuration = parseInt(document.getElementById('musicDurationFixed').value) || 60;
                } else if (durationMode === 'random') {
                    const min = parseInt(document.getElementById('musicDurationMin').value) || 45;
                    const max = parseInt(document.getElementById('musicDurationMax').value) || 120;
                    finalDuration = Math.floor(Math.random() * (max - min + 1)) + min;
                }
                
                logMusicMaster("[" + (i+1) + "/" + prompts.length + "] Gerando... (" + finalDuration + "s)");
                if (prompts.length > 1) updateMusicProgress(i, prompts.length);
                
                try {
                    const response = await fetch("/api/audio/generate", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ prompt: p, engine, duration: finalDuration })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        logMusicMaster("[" + (i+1) + "/" + prompts.length + "] ✅ Sucesso!");
                        successCount++;
                        window.batchGeneratedFiles.push(result.file_url);
                        
                        const trackList = document.getElementById('batchTracksList');
                        const index = window.batchGeneratedFiles.length;
                        const trackHtml = 
                            <div style="background: #1e1e28; padding: 15px; border-radius: 8px; border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; gap: 15px;">
                                <div style="flex: 1;">
                                    <h4 style="color: var(--cyan); margin-top:0; margin-bottom: 10px;">Faixa : ...</h4>
                                    <audio controls style="width: 100%;">
                                        <source src="" type="audio/mpeg">
                                    </audio>
                                </div>
                                <a href="" download class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</a>
                            </div>
                        ;
                        trackList.insertAdjacentHTML('beforeend', trackHtml);

                        if (window.apolloTransferOS) { 
                            window.apolloTransferOS.addItem("audio", result.file_url.split('/').pop(), "Música: " + p.substring(0,20), null, { url: window.location.origin + result.file_url }); 
                        }
                    } else {
                        logMusicMaster("[" + (i+1) + "/" + prompts.length + "] ❌ Erro: " + result.error);
                    }
                } catch(e) {
                    logMusicMaster("[" + (i+1) + "/" + prompts.length + "] ❌ Erro na requisição: " + e);
                }
                
                if (prompts.length > 1) updateMusicProgress(i+1, prompts.length);
            }
            
            musicRunning = false;
            document.getElementById('btnGenerateMusicMaster').style.display = 'block';
            document.getElementById('btnStopMusicMaster').style.display = 'none';
            logMusicMaster("Sessão finalizada! " + successCount + " geradas.");
            
            if (window.batchGeneratedFiles && window.batchGeneratedFiles.length > (prompts.length > 1 ? 1 : 0)) {
                document.getElementById('batchDownloadAllContainer').style.display = 'block';
            }
        }
        window.addEventListener('DOMContentLoaded', () => { if(typeof toggleMusicUI === 'function') toggleMusicUI(); });

