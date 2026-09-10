import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. ADD TAB BUTTON
# Procurando por: <button class="tab-btn" onclick="showTab('audio')">🎤 Áudio</button>
target_btn = '''<button class="tab-btn" onclick="showTab('audio')">🎤 Áudio</button>'''
new_btn = '''<button class="tab-btn" onclick="showTab('audio')">🎤 Áudio</button>\n            <button class="tab-btn" onclick="showTab('music')">🎵 Audio Lab</button>'''
content = content.replace(target_btn, new_btn)

# 2. ADD TAB CONTENT BEFORE <script>
html_tab = '''
        <!-- TAB: AUDIO LAB (MUSIC & SFX) -->
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
                <textarea id="musicPrompt" placeholder="Ex: Batida de trap sombria com graves fortes e sintetizadores..."></textarea>
                
                <div id="lyricsContainer" style="display:none; margin-top: 15px;">
                    <div class="field-label">Letra da Música (Obrigatório para ACE-Step)</div>
                    <textarea id="musicLyrics" placeholder="[Verse 1]\nAcordei cedo pra vencer..."></textarea>
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
                <div id="musicError" style="display:none; color: var(--red); background: #ff475711; padding: 10px; border-radius: 8px; margin-top: 10px; font-family: var(--mono); font-size: 0.8rem;"></div>
            </div>
        </div>
'''
content = content.replace("<script>", html_tab + "\n<script>")

# 3. ADD JS FUNCTIONS
js_logic = '''
        function updateMusicUI() {
            const model = document.getElementById('musicModel').value;
            const modelText = document.getElementById('musicModel').options[document.getElementById('musicModel').selectedIndex].text;
            document.getElementById('musicBadgeModel').textContent = modelText;
            
            const lyricsContainer = document.getElementById('lyricsContainer');
            const refAudioContainer = document.getElementById('refAudioContainer');
            
            if (model === 'ace-step') {
                lyricsContainer.style.display = 'block';
                refAudioContainer.style.display = 'block';
            } else if (model === 'minimax') {
                lyricsContainer.style.display = 'none';
                refAudioContainer.style.display = 'none';
            } else {
                lyricsContainer.style.display = 'none';
                refAudioContainer.style.display = 'block';
            }
        }

        async function generateMusicTest() {
            const model = document.getElementById('musicModel').value;
            const prompt = document.getElementById('musicPrompt').value;
            const lyrics = document.getElementById('musicLyrics').value;
            const refFile = document.getElementById('musicRefFile').files[0];
            
            if (!prompt.trim()) { alert("Digite o prompt!"); return; }
            
            document.getElementById('musicResultCard').style.display = 'block';
            document.getElementById('musicLoading').style.display = 'block';
            document.getElementById('musicOutput').style.display = 'none';
            document.getElementById('musicError').style.display = 'none';
            
            const formData = new FormData();
            formData.append('model', model);
            formData.append('prompt', prompt);
            if (lyrics) formData.append('lyrics', lyrics);
            if (refFile) formData.append('ref_audio', refFile);

            try {
                const response = await fetch('/api/audio/lab_test', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                document.getElementById('musicLoading').style.display = 'none';
                
                if (data.success) {
                    document.getElementById('musicOutput').style.display = 'block';
                    document.getElementById('musicPlayer').src = data.audio_url;
                } else {
                    document.getElementById('musicError').style.display = 'block';
                    document.getElementById('musicError').textContent = data.error || 'Erro.';
                }
            } catch (err) {
                document.getElementById('musicLoading').style.display = 'none';
                document.getElementById('musicError').style.display = 'block';
                document.getElementById('musicError').textContent = err.message;
            }
        }
'''
content = content.replace("function showTab(name) {", js_logic + "\n        function showTab(name) {")

# 4. FIX TABS ARRAY
content = content.replace("const tabs = ['img','vid','audio'];", "const tabs = ['img','vid','audio','music'];")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Sucesso Python!")
