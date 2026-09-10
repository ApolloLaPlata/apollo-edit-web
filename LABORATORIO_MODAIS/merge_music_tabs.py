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
                        🎧 Música Única
                    </label>
                    <label style="flex:1; background:#1a1a2a; padding:10px; border-radius:8px; cursor:pointer; text-align:center;">
                        <input type="radio" name="musicExecMode" value="batch" onchange="toggleMusicUI()"> 
                        🚀 Várias (Em Lote)
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

# We need to replace everything from <div id="tab-music" ... to the end of <div id="tab-batch" ...
# Regex to match from id="tab-music" up to the end of tab-batch
pattern = r'<div id="tab-music".*?<!-- â• â• â•  PAINEL DE PREVIEW'
html = re.sub(pattern, unified_tab_html + '\n        <!-- ═══ PAINEL DE PREVIEW', html, flags=re.DOTALL)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("UI substituída.")
