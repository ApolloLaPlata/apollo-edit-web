import re

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\frontend\modal_ai_studio.html"
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

eleven_lab_html = """
            <!-- INICIO ELEVEN LAB -->
            <div class="card" style="margin-top: 20px;">
                <div class="card-title">🎙️ Apollo Eleven Lab <span class="badge">Conta 10</span></div>
                <div style="font-size: 0.9rem; color: var(--text-dim); margin-bottom: 15px;">Ambiente de teste unificado de TTS (XTTS, MOSS, Qwen, etc.)</div>
                
                <div class="field-label">Motor TTS</div>
                <select id="elevenModel" class="input-field" style="width:100%; margin-bottom: 15px;">
                    <option value="Qwen-TTS">Qwen-TTS</option>
                    <option value="XTTS">XTTS</option>
                    <option value="Moss-TTS">Moss-TTS</option>
                    <option value="F5-TTS">F5-TTS</option>
                    <option value="Fish-Speech">Fish-Speech</option>
                    <option value="Melo-TTS">Melo-TTS</option>
                    <option value="ChatTTS">ChatTTS</option>
                    <option value="CosyVoice">CosyVoice</option>
                    <option value="OpenVoice">OpenVoice</option>
                </select>
                
                <div class="field-label">Texto para Falar</div>
                <textarea id="elevenText" class="input-field" rows="3" style="width:100%; resize:vertical; margin-bottom: 15px;">Olá, este é o laboratório de testes do Apollo.</textarea>
                
                <div class="field-label">🎭 Prompt de Interpretação / Humor (Instruct)</div>
                <textarea id="elevenInstruct" class="input-field" rows="2" style="width:100%; resize:vertical; margin-bottom: 15px;" placeholder="Ex: Fale com raiva, tom irônico, chorando... (Suportado por modelos como Qwen, F5, etc)"></textarea>
                
                <div class="field-label">Voz Padrão (Catálogo de Clonagem)</div>
                <select id="elevenVoice" class="input-field" style="width:100%; margin-bottom: 15px;">
                    <option value="narrador_ref">Narrador Padrão (XTTS)</option>
                    <option value="roxingo_ref">Roxingo (XTTS)</option>
                    <option value="rafael_descargas">Rafael (Descargas)</option>
                    <option value="female_clean_ref">Feminina Clean</option>
                    <option value="custom">Upload/Outra (Selecione abaixo)</option>
                </select>
                
                <div class="field-label">Ou: Upload de Voz Clonada (Substitui padrão)</div>
                <div class="file-input-wrap">
                    <label for="elevenRefAudio" class="file-label">📂 Escolher arquivo</label>
                    <input type="file" id="elevenRefAudio" accept="audio/*" onchange="document.getElementById('elevenRefFileName').innerText = this.files[0] ? this.files[0].name : 'Nenhum arquivo selecionado'; document.getElementById('elevenVoice').value='custom';">
                    <span class="file-name" id="elevenRefFileName">Nenhum arquivo selecionado</span>
                </div>
                
                <div style="display:flex; gap: 15px; margin-top:15px;">
                    <div style="flex:1;">
                        <div class="field-label">Temperatura</div>
                        <input type="range" id="elevenTemp" min="0.1" max="1.5" step="0.1" value="0.7" style="width:100%;">
                    </div>
                    <div style="flex:1;">
                        <div class="field-label">Velocidade</div>
                        <input type="range" id="elevenSpeed" min="0.5" max="2.0" step="0.1" value="1.0" style="width:100%;">
                    </div>
                </div>
                
                <button class="btn btn-primary" id="btnElevenGenerate" onclick="generateElevenVoice()" style="margin-top:20px; width:100%;">
                    🎙️ Gerar Voz (Nuvem Conta 10)
                </button>
                
                <div class="log-box" id="elevenStatus" style="margin-top:15px;">Aguardando comando...</div>
                
                <div id="elevenResultBox" style="margin-top:15px; display:none; background:#0d0d15; border-radius:8px; padding:12px; border:1px solid var(--border);">
                    <audio id="elevenAudioPlayer" controls style="width:100%; outline:none; margin-bottom:10px;"></audio>
                </div>
            </div>
            <!-- FIM ELEVEN LAB -->
"""

# Check if the eleven lab is already in the HTML. If so, remove it cleanly.
content = re.sub(r'<!-- INICIO ELEVEN LAB -->.*?<!-- FIM ELEVEN LAB -->', '', content, flags=re.DOTALL)

# Find the end of the first card in tab-audio
# We can search for the end of the transcription result div and the button inside tab-audio
# Since encoding might be messed up, we search for a stable substring
pattern = r'(Copiar Texto</button>\s*</div>\s*)(</div>\s*</div>)'
match = re.search(pattern, content)
if match:
    # Inject it inside the tab-audio div, right after the transcription card
    # Wait, the transcription card ends with `Copiar Texto</button>\n </div>`.
    # And then there's another closing `</div>` for tab-audio.
    
    # Actually, a simpler pattern:
    # Look for: <div id="tab-music"
    parts = content.split('<div id="tab-music"')
    if len(parts) == 2:
        # The first part contains tab-audio. We want to insert our card right before the closing </div> of tab-audio.
        # Let's find the last </div> before '<div id="tab-music"'
        last_div_index = parts[0].rfind('</div>')
        if last_div_index != -1:
            parts[0] = parts[0][:last_div_index] + eleven_lab_html + '\n' + parts[0][last_div_index:]
            content = '<div id="tab-music"'.join(parts)
            print("Injected HTML successfully using tab-music boundary.")
else:
    print("Failed to find anchor pattern for HTML injection.")
    
# Make sure the Audio tab is visible. 
# Search for: <div id="tab-audio" style="display:none;"> and change it to <div id="tab-audio">
# We don't want to change the div's display here since it's controlled by JS, BUT we should make sure the button has NO display:none.
content = content.replace("showTab('audio')\" style=\"display: none;\"", "showTab('audio')\"")

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
