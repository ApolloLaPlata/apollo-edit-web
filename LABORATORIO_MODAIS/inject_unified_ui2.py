import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    code = f.read()

unified_ui = '''        <!-- TAB: MÚSICA -->
        <div id="tab-music" style="display:none;">
            <div class="card">
                <div class="card-title">🎵 Gerador de Música / SFX</div>
                
                <div class="field-label">Modo de Execução</div>
                <div style="display:flex; gap:10px; margin-bottom:15px;">
                    <label><input type="radio" name="musicExecMode" value="single" checked onclick="toggleMusicUI()"> 🎵 Única</label>
                    <label><input type="radio" name="musicExecMode" value="batch" onclick="toggleMusicUI()"> 🚀 Em Lote (Várias)</label>
                </div>
                
                <div class="field-label">Motor de Inteligência Artificial</div>
                <select id="musicModel" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
                    <option value="acestep">ACE-Step 1.5 (Melhor para batidas e estilos musicais)</option>
                    <option value="sa3">Stable Audio 3 (Melhor para Efeitos Sonoros e Sound Design)</option>
                    <option value="minimax">MiniMax Music3 (Melhor para Vocais e Músicas Completas)</option>
                </select>

                <div class="field-label">Estilo / Tipo de Faixa</div>
                <select id="musicStyle" onchange="toggleMusicUI()" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
                    <option value="instrumental">🎶 Apenas Instrumental</option>
                    <option value="vocal">🎤 Com Vocais/Letra</option>
                    <option value="auto">🤖 Automático (Deixar o modelo decidir)</option>
                </select>
                
                <!-- SINGLE AREA -->
                <div id="musicSingleArea" style="margin-bottom:15px;">
                    <div class="field-label">Descreva o som desejado (Prompt de Estilo)</div>
                    <textarea id="musicSinglePrompt" placeholder="Ex: Uma trilha sonora épica de suspense..." style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:60px;"></textarea>
                    
                    <div id="musicSingleLyricsContainer" style="display:none; margin-top:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="field-label" style="margin:0;">Letra da Música</div>
                            <button class="btn btn-primary" id="btnAutoTag" onclick="autoTagLyrics()" style="font-size:10px; padding:4px 8px;">🪄 Auto-Tag (IA)</button>
                        </div>
                        <textarea id="musicSingleLyrics" placeholder="Digite a letra aqui..." style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:100px; margin-top:5px;"></textarea>
                    </div>
                </div>
                
                <!-- BATCH AREA -->
                <div id="musicBatchArea" style="display:none; margin-bottom:15px; border:1px dashed var(--border); padding:10px; border-radius:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h4 style="margin:0; color:var(--cyan);">🚀 Lote IA</h4>
                    </div>
                    <div style="display:flex; gap:10px; margin-bottom:10px;">
                        <input type="text" id="aiBatchTheme" placeholder="Tema (ex: Cyberpunk, Trap...)" style="flex:1; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                        <input type="number" id="aiBatchCount" value="3" min="2" max="10" style="width:60px; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                        <button class="btn btn-primary" id="btnAIGenerateBatch" onclick="generateBatchIdeas()">✨ Gerar Ideias</button>
                    </div>
                    
                    <div class="field-label">Lista de Prompts de Estilo (Um por linha)</div>
                    <textarea id="musicBatchPrompts" placeholder="Linha 1: Prompt da primeira música\nLinha 2: Prompt da segunda música..." style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:80px; margin-bottom:10px;"></textarea>
                    
                    <div id="musicBatchLyricsContainer" style="display:none;">
                        <div class="field-label">Lista de Letras (Separadas por ===)</div>
                        <textarea id="musicBatchLyrics" placeholder="[Verse 1]\n...\n===\n[Verse 1]\n..." style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; min-height:120px;"></textarea>
                    </div>
                </div>
                
                <div class="field-label">Modo de Duração</div>
                <select id="musicDurationMode" onchange="toggleMusicUI()" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
                    <option value="fixed">Fixo (Todos com a mesma duração)</option>
                    <option value="random">Aleatório (Entre Min e Max)</option>
                </select>
                
                <div id="musicDurationFixedArea" style="margin-bottom:15px;">
                    <div class="field-label">Duração (Segundos)</div>
                    <input type="number" id="musicDurationFixed" value="30" min="5" max="120" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                </div>
                
                <div id="musicDurationRandomArea" style="display:none; gap:10px; margin-bottom:15px;">
                    <div style="flex:1;">
                        <div class="field-label">Min (s)</div>
                        <input type="number" id="musicDurationMin" value="15" min="5" max="120" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                    </div>
                    <div style="flex:1;">
                        <div class="field-label">Max (s)</div>
                        <input type="number" id="musicDurationMax" value="45" min="5" max="120" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                    </div>
                </div>
                
                <button class="btn btn-primary" id="btnGenerateMusicMaster" onclick="generateMusicMaster()" style="width:100%;">
                    🎧 Iniciar Geração (Conta 9)
                </button>
                <button class="btn btn-primary" id="btnStopMusicMaster" onclick="stopMusicMaster()" style="width:100%; display:none; background:#ff4444; border-color:#ff4444; margin-top:8px;">
                    ⛔ Cancelar Processo
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

# Use find to locate the start of tab-music and the end of the sidebar
start_idx = code.find('<!-- TAB: M')
end_idx = code.find('</aside>')

if start_idx != -1 and end_idx != -1:
    new_code = code[:start_idx] + unified_ui + '\n    ' + code[end_idx:]
    with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("UI Unificada injetada!")
else:
    print("Não encontrou os marcadores.")
