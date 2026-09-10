import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Vamos achar todo o tab-music e reconstruir direito.
start_tab = content.find('<!-- TAB: AUDIO LAB (MUSIC & SFX) -->')
end_tab = content.find('<!-- fim tab-music -->')

if end_tab == -1:
    # Se não tiver tag de fim, procura o próximo <div id="tab-audio"> ou algo
    end_tab = content.find('<div id="tab-audio"', start_tab)

if start_tab != -1 and end_tab != -1:
    new_tab = '''<!-- TAB: AUDIO LAB (MUSIC & SFX) -->
        <div id="tab-music" style="display:none;">
            <div class="card">
                <div class="card-title">🎵 Audio Lab <span class="badge" id="musicBadgeModel">Stable Audio 3</span></div>
                
                <div class="field-label">Escolha o Motor Acústico</div>
                <select id="musicModel" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;" onchange="updateMusicUI()">
                    <option value="sa3">Stable Audio 3 Medium (Instrumental & SFX)</option>
                    <option value="minimax">MiniMax (Voz Pura & Narração)</option>
                    <option value="ace-step">ACE-Step (Música Completa & Letra)</option>
                </select>
                
                <div class="field-label">Prompt (Descreva o som ou a voz)</div>
                <textarea id="musicPrompt" placeholder="Ex: Batida de trap sombria com graves fortes..."></textarea>
                
                <div id="lyricsContainer" style="margin-top: 15px;">
                    <div class="field-label">Letra da Música (Opcional)</div>
                    <textarea id="musicLyrics" placeholder="[Verse 1]\nAcordei cedo pra vencer..."></textarea>
                </div>
                
                <div id="timeContainer" style="margin-top: 15px;">
                    <div class="field-label">Duração (Segundos)</div>
                    <input type="number" id="musicDuration" value="30" min="1" max="180" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                </div>
                
                <div id="refAudioContainer" style="margin-top: 15px;">
                    <div class="field-label">Áudio de Referência (Opcional - Estilo ou Continuação)</div>
                    <div class="file-input-wrap">
                        <label for="musicRefFile" class="file-label">📁 Escolher arquivo</label>
                        <span class="file-name" id="musicRefFileName">Nenhum selecionado...</span>
                        <input type="file" id="musicRefFile" style="display:none;" accept="audio/*" onchange="document.getElementById('musicRefFileName').textContent = this.files[0] ? this.files[0].name : 'Nenhum selecionado...'">
                    </div>
                </div>
                
                <button class="generate-btn" id="btnGenMusic" onclick="generateMusicTest()" style="margin-top: 20px;">
                    <span class="btn-icon">⚡</span> TESTAR GERAÇÃO DE ÁUDIO
                </button>
            </div>
            
            <div class="card" id="musicResultCard" style="display:none; margin-top: 20px;">
                <div class="card-title">🎧 Resultado do Teste</div>
                <div id="musicLoading" style="text-align:center; padding: 20px; display:none;">
                    <div class="loader" style="margin:0 auto;"></div>
                    <div style="margin-top:10px; color:var(--cyan);">Processando via Modal...</div>
                </div>
                <div id="musicOutput" style="display:none; text-align: center;">
                    <audio id="musicPlayer" controls style="width: 100%; margin-top: 10px;"></audio>
                </div>
                <pre id="musicError" style="display:none; color: var(--red); background: #ff475711; padding: 10px; border-radius: 8px; margin-top: 10px; font-family: var(--mono); font-size: 0.8rem; white-space: pre-wrap; overflow-x: auto;"></pre>
            </div>
        </div>
        
        <!-- fim tab-music -->
        '''
    
    content = content[:start_tab] + new_tab + content[end_tab:]

# Corrigir o JS catch
if 'document.getElementById(\'musicError\').textContent = err.message;' in content:
    content = content.replace("document.getElementById('musicError').textContent = data.error || 'Erro.';", "document.getElementById('musicError').textContent = JSON.stringify(data, null, 2);")
    content = content.replace("document.getElementById('musicError').textContent = err.message;", "document.getElementById('musicError').textContent = 'CRASH FETCH: ' + err.message;")
    
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("HTML reescrito para arrumar os duplicados e expor todos os logs!")
