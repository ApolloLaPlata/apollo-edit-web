import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the "Em Lote" tab button
html = re.sub(
    r'<button class="tab-btn" onclick="showTab\(\'batch\'\)">.*?<\/button>',
    '',
    html
)

# 2. Replace tab-music and tab-batch with unified tab-music
unified_tab_html = '''
        <!-- TAB: MÚSICA (UNIFICADA - SINGLE E LOTE) -->
        <div id="tab-music" style="display:none;">
            <div class="card">
                <div class="card-title">🎵 Gerador de Música / SFX</div>
                
                <div class="field-label">Motor de Inteligência Artificial</div>
                <select id="musicModel" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
                    <option value="sa3">Stable Audio 3 (Melhor para Qualidade/Instrumental)</option>
                    <option value="minimax">MiniMax Music3 (Melhor para Vocais/Músicas Completas)</option>
                    <option value="acestep">ACE-Step 1.5 (Batidas Rápidas)</option>
                </select>

                <div style="display:flex; gap:10px; margin-bottom: 15px;">
                    <label style="flex:1; background:#1a1a2a; padding:10px; border-radius:8px; cursor:pointer; text-align:center;">
                        <input type="radio" name="musicExecMode" value="single" checked onchange="toggleMusicUI()"> 
                        🎧 Faixa Única
                    </label>
                    <label style="flex:1; background:#1a1a2a; padding:10px; border-radius:8px; cursor:pointer; text-align:center;">
                        <input type="radio" name="musicExecMode" value="batch" onchange="toggleMusicUI()"> 
                        🚀 Várias Faixas (Em Lote)
                    </label>
                </div>

                <div class="field-label">Estilo / Letra</div>
                <select id="musicStyle" onchange="toggleMusicUI()" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
                    <option value="instrumental">🎶 Apenas Instrumental</option>
                    <option value="vocal">🎤 Com Vocais (Definir Letras)</option>
                </select>

                <!-- Área Single -->
                <div id="musicSingleArea">
                    <div class="field-label">Prompt de Estilo Musical</div>
                    <textarea id="musicSinglePrompt" placeholder="Ex: Epic cyberpunk synthwave, driving bassline..." style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:60px; margin-bottom: 15px;"></textarea>
                    
                    <div id="musicSingleLyricsContainer" style="display:none;">
                        <div class="field-label">Letra da Música (Opcional)</div>
                        <textarea id="musicSingleLyrics" placeholder="[Verse]\nWalking in the rain...\n\n[Chorus]\nAnd I feel no pain!" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:120px; margin-bottom: 15px;"></textarea>
                    </div>
                </div>

                <!-- Área Batch (Lote) -->
                <div id="musicBatchArea" style="display:none;">
                    <div style="display:flex; gap:10px; margin-bottom: 15px;">
                        <div style="flex:1;">
                            <div class="field-label">Lista de Estilos (1 por linha)</div>
                            <textarea id="musicBatchPrompts" placeholder="Estilo 1...\nEstilo 2..." style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:150px; white-space:pre;"></textarea>
                        </div>
                        <div id="musicBatchLyricsContainer" style="flex:1; display:none;">
                            <div class="field-label">Letras (Separar por ===)</div>
                            <textarea id="musicBatchLyrics" placeholder="Letra 1...\n===\nLetra 2..." style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:150px; white-space:pre;"></textarea>
                        </div>
                    </div>
                </div>

                <div class="field-label">Duração da Música</div>
                <select id="musicDurationMode" onchange="toggleMusicUI()" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
                    <option value="auto">🤖 Automático (Baseado na Letra / Padrão Suno)</option>
                    <option value="fixed">⏳ Tamanho Definido Fixo</option>
                    <option value="random">🎲 Máxima e Mínima (Aleatório)</option>
                </select>
                
                <div id="musicDurationFixedArea" style="display:none; margin-bottom: 15px;">
                    <input type="number" id="musicDurationFixed" value="60" min="5" max="300" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                </div>
                
                <div id="musicDurationRandomArea" style="display:none; gap:10px; margin-bottom: 15px;">
                    <div style="flex:1;">
                        <span style="font-size:0.7rem; color:var(--text-dim);">Mínimo</span>
                        <input type="number" id="musicDurationMin" value="45" min="5" max="300" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                    </div>
                    <div style="flex:1;">
                        <span style="font-size:0.7rem; color:var(--text-dim);">Máximo</span>
                        <input type="number" id="musicDurationMax" value="120" min="5" max="300" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                    </div>
                </div>
                
                <button class="btn btn-primary" id="btnGenerateMusicMaster" onclick="generateMusicMaster()" style="width:100%; font-size:1.1rem; padding:12px;">
                    🚀 Iniciar Geração de Música
                </button>
                <button class="btn btn-primary" id="btnStopMusicMaster" onclick="stopMusicMaster()" style="width:100%; display:none; background:#ff4444; border-color:#ff4444; margin-top:8px;">
                    🛑 Cancelar Geração
                </button>
                <div class="log-box" id="musicMasterStatus" style="margin-top:10px;">Aguardando...</div>
                
                <div id="musicProgressContainer" style="display:none; margin-top:10px;">
                    <div style="width:100%; background:#2a2a35; border-radius:4px; height:10px;">
                        <div id="musicProgressBar" style="width:0%; background:var(--cyan); height:10px; border-radius:4px; transition:width 0.3s;"></div>
                    </div>
                    <div id="musicProgressText" style="text-align:center; font-size:10px; margin-top:4px; color:var(--text-dim);">0/0</div>
                </div>
            </div>
        </div>
'''

pattern = r'<div id="tab-music".*?<!-- â• â• â•  PAINEL DE PREVIEW'
html = re.sub(pattern, unified_tab_html + '\n        <!-- ═══ PAINEL DE PREVIEW', html, flags=re.DOTALL)


# JS REPLACEMENT
new_js = '''
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
                prompts = rawPrompts.split('\\n').map(p => p.trim()).filter(p => p);
                
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
                        p += "\\n\\nLyrics:\\n" + lyrics[i];
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
'''

# We must replace all old music/batch logic in JS
# Remove old generateMusicStudio
html = re.sub(r'async function generateMusicStudio\(\) \{.*?\n        }', '', html, flags=re.DOTALL)
# Remove old batch logic
html = re.sub(r'function toggleBatchMode\(\) \{.*?function stopBatch\(\) \{.*?\n        }', '', html, flags=re.DOTALL)

# Insert the new logic just before the end of the script tag
html = html.replace('</script>', new_js + '\n</script>')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
