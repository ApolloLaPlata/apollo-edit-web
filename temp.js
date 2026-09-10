
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

function showTab(name) {
    ['img','vid','audio'].forEach(t => {
        document.getElementById('tab-'+t).style.display = (t === name) ? 'block' : 'none';
        document.querySelectorAll('.tab-btn').forEach((b,i) => {
            const tabs = ['img','vid','audio'];
            b.classList.toggle('active', tabs[i] === name);
        });
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

