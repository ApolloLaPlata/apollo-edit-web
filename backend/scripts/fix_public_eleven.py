import re
import os

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html"
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# I will replace the entire tab-voice panel with my new Eleven Lab one.
# First, let's find the boundaries of tab-voice.
# It starts with `<div id="tab-voice"` and ends when `<div id="tab-music"` starts.

eleven_lab_html = """
        <!-- =================== ABA VOZ (TTS / CLONAGEM) =================== -->
        <div id="tab-voice" style="display:none;">
            <div class="panel">
                <div class="panel-header">🎙️ SÍNTESE DE VOZ E CLONAGEM <span class="badge" style="background:#55f; padding:2px 8px; border-radius:12px; font-size:12px; margin-left:10px;">Conta 10 (Eleven Lab)</span></div>
                
                <div class="form-group">
                    <div class="field-label">Motor TTS (Engine)</div>
                    <select class="input-dark" id="voiceEngineSelect" style="width:100%; padding:10px; border-radius:8px; background:#0d0d15; color:var(--text); border:1px solid var(--border); margin-bottom:15px;">
                        <option value="Qwen-TTS">Qwen-TTS (Instrucional / Melhor Atuação)</option>
                        <option value="F5-TTS" selected>F5-TTS (Zero-Shot Cloning Rápido)</option>
                        <option value="Moss-TTS">MOSS-TTS 8B (Clonagem Alta Qualidade)</option>
                        <option value="XTTS">XTTS v2 (Clonagem Rápida Padrão)</option>
                        <option value="Fish-Speech">Fish-Speech</option>
                        <option value="Melo-TTS">Melo-TTS</option>
                        <option value="ChatTTS">ChatTTS</option>
                        <option value="CosyVoice">CosyVoice</option>
                        <option value="OpenVoice">OpenVoice</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <div class="field-label">Texto / Roteiro (O que o oráculo deverá narrar)</div>
                    <textarea class="input-dark" id="voiceText" rows="4" placeholder="Digite o texto principal..." style="width:100%; padding:10px; border-radius:8px; background:#0d0d15; color:var(--text); border:1px solid var(--border); margin-bottom:15px;"></textarea>
                </div>

                <div class="form-group">
                    <div class="field-label">🎭 Instrução de Interpretação / Humor (Instruct)</div>
                    <textarea class="input-dark" id="voiceInstruct" rows="2" placeholder="Ex: Fale com raiva, tom irônico, chorando... (Suportado por Qwen, etc)" style="width:100%; padding:10px; border-radius:8px; background:#0d0d15; color:var(--text); border:1px solid var(--border); margin-bottom:15px;"></textarea>
                </div>
                
                <div class="form-group">
                    <div class="field-label">Voz Base (Catálogo)</div>
                    <select class="input-dark" id="voiceIdSelect" style="width:100%; padding:10px; border-radius:8px; background:#0d0d15; color:var(--text); border:1px solid var(--border); margin-bottom:15px;">
                        <option value="narrador_ref">Narrador Padrão (XTTS)</option>
                        <option value="roxingo_ref">Roxingo (XTTS)</option>
                        <option value="rafael_descargas">Rafael (Descargas)</option>
                        <option value="female_clean_ref">Feminina Clean</option>
                        <option value="custom">-- Use apenas o Áudio de Referência abaixo --</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <div class="field-label">OU Clonar Nova Voz (Upload de Áudio de Referência)</div>
                    <div class="file-input-wrap">
                        <label for="voiceRefFile" class="file-label">📁 Escolher Áudio</label>
                        <input type="file" id="voiceRefFile" accept="audio/*,video/*,.mpeg,.mp4,.ogg,.m4a,.webm,.wav,.mp3" onchange="document.getElementById('voiceRefFileName').innerText = this.files.length > 0 ? this.files[0].name : 'Nenhum arquivo selecionado'; document.getElementById('voiceIdSelect').value='custom';">
                        <span class="file-name" id="voiceRefFileName">Nenhum arquivo selecionado</span>
                    </div>
                </div>

                <div class="form-group" style="margin-top: 15px;">
                    <div class="field-label">📝 Texto de Referência (Obrigatório para F5-TTS e Qwen)</div>
                    <textarea class="input-dark" id="voiceRefText" rows="2" placeholder="Digite aqui a transcrição exata do áudio de referência (Voz Clonada)." style="width:100%; padding:10px; border-radius:8px; background:#0d0d15; color:var(--text); border:1px solid var(--border); margin-bottom:15px;"></textarea>
                </div>

                <div style="display:flex; gap: 15px; margin-top:15px; margin-bottom: 20px;">
                    <div style="flex:1;">
                        <div class="field-label">Temperatura</div>
                        <input type="range" id="voiceTemp" min="0.1" max="1.5" step="0.1" value="0.7" style="width:100%;">
                    </div>
                    <div style="flex:1;">
                        <div class="field-label">Velocidade</div>
                        <input type="range" id="voiceSpeed" min="0.5" max="2.0" step="0.1" value="1.0" style="width:100%;">
                    </div>
                </div>

                <button id="btnGenerateVoice" class="btn btn-primary btn-block" style="width:100%; padding:15px; font-size:16px; border-radius:8px; background: #00bcd4; color: #fff; font-weight: bold;" onclick="generateVoice()">
                    <span class="icon">🎙️</span> Gerar Voz (Conta 10)
                </button>
            </div>
        </div>
"""

# Extract the content before tab-voice and after the end of tab-voice
parts = content.split('<div id="tab-voice"')
if len(parts) >= 2:
    before_tab_voice = parts[0]
    # Find the next tab which is tab-music
    sub_parts = parts[1].split('<div id="tab-music"', 1)
    if len(sub_parts) == 2:
        after_tab_voice = '<div id="tab-music"' + sub_parts[1]
        
        # Replace the entire tab-voice
        content = before_tab_voice + eleven_lab_html + "\n" + after_tab_voice
        print("UI Replaced in public HTML successfully.")

# Now we need to update the JavaScript function generateVoice()
# Let's replace the whole async function generateVoice() { ... }
new_js = """        async function generateVoice() {
            const text = document.getElementById('voiceText').value.trim();
            if (!text) return alert("Digite um texto para gerar a voz.");
            
            const engineId = document.getElementById('voiceEngineSelect').value;
            const instruct = document.getElementById('voiceInstruct').value;
            const refText = document.getElementById('voiceRefText').value;
            const voiceSelect = document.getElementById('voiceIdSelect').value;
            const refFile = document.getElementById('voiceRefFile').files[0];
            const temp = document.getElementById('voiceTemp').value;
            const speed = document.getElementById('voiceSpeed').value;
            
            const btn = document.getElementById('btnGenerateVoice');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="icon">⏳</span> Gerando Voz na Conta 10...';
            btn.disabled = true;
            
            let base64Audio = null;
            let voiceName = null;
            
            try {
                if (refFile) {
                    base64Audio = await new Promise((resolve, reject) => {
                        const reader = new FileReader();
                        reader.onload = () => resolve(reader.result.split(',')[1]);
                        reader.onerror = error => reject(error);
                        reader.readAsDataURL(refFile);
                    });
                } else if (voiceSelect !== 'custom') {
                    voiceName = voiceSelect;
                }
                
                const payload = {
                    model: engineId,
                    text: text,
                    instruct: instruct,
                    ref_text: refText,
                    temperature: parseFloat(temp),
                    speed: parseFloat(speed),
                    voice_name: voiceName,
                    ref_audio_base64: base64Audio
                };
                
                const response = await fetch('/api/studio/modal/eleven_lab', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    const err = await response.text();
                    throw new Error(`Erro ${response.status}: ${err}`);
                }
                
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                // Show result in the visualizer
                const resultBox = document.getElementById('resultVisualizer');
                if (resultBox) {
                    resultBox.innerHTML = `
                        <div style="background:#1a1a24; padding:20px; border-radius:12px; border:1px solid #333; text-align:center;">
                            <h3 style="color:#00bcd4; margin-bottom:15px;">✅ Áudio Gerado com Sucesso (${engineId})</h3>
                            <audio controls style="width:100%; outline:none;" src="${url}"></audio>
                            <a href="${url}" download="voz_gerada.wav" class="btn btn-primary" style="display:inline-block; margin-top:15px;"><span class="icon">💾</span> Baixar Áudio</a>
                        </div>
                    `;
                }
                
            } catch (err) {
                console.error(err);
                alert('❌ Erro: ' + err.message);
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }"""

# Find and replace the old function in content
old_func_pattern = r'\s*async function generateVoice\(\) \{.*?\n        \}'
content = re.sub(old_func_pattern, '\n' + new_js, content, flags=re.DOTALL)

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated Javascript logic in public HTML.")
