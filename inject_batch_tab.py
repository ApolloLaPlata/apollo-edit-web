import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Inject the button
    button_html = '<button class="tab-btn" onclick="showTab(\'batch\')">?? Em Lote</button>'
    if '?? Em Lote' not in content:
        content = content.replace('<button class="tab-btn" onclick="showTab(\'music\')">?? Música</button>', 
                                  '<button class="tab-btn" onclick="showTab(\'music\')">?? Música</button>\n            ' + button_html)
    
    # 2. Update showTab javascript
    old_js = "['img','vid','audio','music'];"
    new_js = "['img','vid','audio','music', 'batch'];"
    if new_js not in content:
        content = content.replace(old_js, new_js)
        
    old_js2 = "['img', 'vid', 'audio', 'music']"
    new_js2 = "['img', 'vid', 'audio', 'music', 'batch']"
    if new_js2 not in content:
        content = content.replace(old_js2, new_js2)

    # 3. Inject the Tab HTML right before </aside>
    tab_html = '''
        <!-- TAB: BATCH -->
        <div id="tab-batch" style="display:none;">
            <div class="card">
                <div class="card-title">?? Gerador de Música em Lote</div>
                
                <div class="field-label">Motor de Inteligência Artificial</div>
                <select id="batchModel" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
                    <option value="acestep">ACE-Step 1.5</option>
                    <option value="sa3">Stable Audio 3</option>
                    <option value="minimax">MiniMax Music3</option>
                </select>

                <div class="field-label">Lista de Prompts (um por linha)</div>
                <textarea id="batchPrompts" placeholder="Linha 1: Prompt da primeira música\nLinha 2: Prompt da segunda música..." style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:120px; margin-bottom: 15px;"></textarea>
                
                <div class="field-label">Duração (Segundos)</div>
                <input type="number" id="batchDuration" value="30" min="5" max="120" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
                
                <button class="btn btn-primary" id="btnGenerateBatch" onclick="generateBatch()" style="width:100%;">
                    ?? Iniciar Fila de Geração
                </button>
                <button class="btn btn-primary" id="btnStopBatch" onclick="stopBatch()" style="width:100%; display:none; background:#ff4444; border-color:#ff4444; margin-top:8px;">
                    ?? Cancelar Fila
                </button>
                <div class="log-box" id="batchStatus" style="margin-top:10px;">Aguardando...</div>
                
                <div id="batchProgressContainer" style="display:none; margin-top:10px;">
                    <div style="width:100%; background:#2a2a35; border-radius:4px; height:10px;">
                        <div id="batchProgressBar" style="width:0%; background:var(--cyan); height:10px; border-radius:4px; transition:width 0.3s;"></div>
                    </div>
                    <div id="batchProgressText" style="text-align:center; font-size:10px; margin-top:4px; color:var(--text-dim);">0/0</div>
                </div>
            </div>
        </div>
'''
    if 'id="tab-batch"' not in content:
        content = content.replace('</aside>', tab_html + '\n    </aside>')

    # 4. Inject the javascript logic
    batch_js = '''
        // --- BATCH GENERATION LOGIC ---
        let batchRunning = false;
        
        async function generateBatch() {
            const raw = document.getElementById('batchPrompts').value.trim();
            if (!raw) {
                alert("Insira ao menos um prompt!");
                return;
            }
            const prompts = raw.split('\\n').map(p => p.trim()).filter(p => p);
            if (prompts.length === 0) return;
            
            const engine = document.getElementById('batchModel').value;
            const duration = document.getElementById('batchDuration').value;
            
            document.getElementById('btnGenerateBatch').style.display = 'none';
            document.getElementById('btnStopBatch').style.display = 'block';
            document.getElementById('batchProgressContainer').style.display = 'block';
            
            batchRunning = true;
            let successCount = 0;
            
            for (let i = 0; i < prompts.length; i++) {
                if (!batchRunning) {
                    logBatch(Processo cancelado na música .);
                    break;
                }
                
                const p = prompts[i];
                logBatch([/] Gerando: ...);
                updateBatchProgress(i, prompts.length);
                
                try {
                    const response = await fetch("/api/audio/generate", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ prompt: p, engine, duration })
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        logBatch([/] ? Sucesso!);
                        successCount++;
                        
                        if (window.apolloTransferOS) { 
                            window.apolloTransferOS.addItem("audio", result.file_url.split('/').pop(), "Lote: " + p.substring(0,20), null, { url: window.location.origin + result.file_url }); 
                        }
                    } else {
                        logBatch([/] ? Erro: );
                    }
                } catch (e) {
                    logBatch([/] ? Erro Rede: );
                }
                
                updateBatchProgress(i+1, prompts.length);
            }
            
            batchRunning = false;
            document.getElementById('btnGenerateBatch').style.display = 'block';
            document.getElementById('btnStopBatch').style.display = 'none';
            
            if (successCount === prompts.length) {
                logBatch(? Lote concluído!  músicas geradas.);
            } else {
                logBatch(?? Lote finalizado. / com sucesso.);
            }
        }
        
        function stopBatch() {
            batchRunning = false;
            logBatch("Cancelamento solicitado (aguarde a atual terminar)...");
        }
        
        function logBatch(msg) {
            const box = document.getElementById('batchStatus');
            box.innerText = msg;
        }
        
        function updateBatchProgress(current, total) {
            const perc = (current / total) * 100;
            document.getElementById('batchProgressBar').style.width = perc + '%';
            document.getElementById('batchProgressText').innerText = ${current}/;
        }
'''
    if 'function generateBatch' not in content:
        content = content.replace('</script>', batch_js + '\n</script>')
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

process_file('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/modal_ai_studio.html')
process_file('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html')
process_file('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/frontend/modal_ai_studio.html')
process_file('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/frontend/modal_ai_studio.html')
print("Injetado com sucesso!")
