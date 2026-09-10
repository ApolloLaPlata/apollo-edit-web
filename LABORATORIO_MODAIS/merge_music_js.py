import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

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
            
            // Build visual list container
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
                    logMusicMaster("[" + (i+1) + "/" + prompts.length + "] ❌ Erro na requisição");
                }
                
                if (prompts.length > 1) updateMusicProgress(i+1, prompts.length);
            }
            
            musicRunning = false;
            document.getElementById('btnGenerateMusicMaster').style.display = 'block';
            document.getElementById('btnStopMusicMaster').style.display = 'none';
            logMusicMaster("Sessão finalizada! " + successCount + " geradas.");
            
            if (window.batchGeneratedFiles && window.batchGeneratedFiles.length > (prompts.length > 1 ? 1 : 0)) {
                // Só mostra o botão baixar tudo se for lote ou mais de 1
                document.getElementById('batchDownloadAllContainer').style.display = 'block';
            }
        }
        
        // Ensure UI matches default state on load
        window.addEventListener('DOMContentLoaded', () => { toggleMusicUI(); });
'''

# Delete generateMusicStudio, toggleBatchMode, stopBatch, generateBatch, updateBatchProgress, logBatch
html = re.sub(r'async function generateMusicStudio\(\).*?// â”€â”€â”€', '// â”€â”€â”€', html, flags=re.DOTALL)
html = re.sub(r'function toggleBatchMode\(\).*?downloadAllBatchFiles\(\) \{.*?\n        }', '', html, flags=re.DOTALL)

# Insert the new JS logic at the end of the script before downloadAllBatchFiles
html = html.replace('function downloadAllBatchFiles()', new_js + '\n        function downloadAllBatchFiles()')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("JS substituído.")
