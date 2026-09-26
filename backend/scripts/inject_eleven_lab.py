import os

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\frontend\modal_ai_studio.html"

# Read file
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Define the HTML to inject
eleven_lab_html = """
            <div class="card" style="margin-top: 20px;">
                <div class="card-title">🎙️ Apollo Eleven Lab <span class="badge">Conta 10</span></div>
                <div style="font-size: 0.9rem; color: var(--text-dim); margin-bottom: 15px;">Ambiente de teste de clonagem unificado (XTTS, MOSS, F5, etc.)</div>
                
                <div class="field-label">Motor TTS</div>
                <select id="elevenModel" class="input-field" style="width:100%; margin-bottom: 15px;">
                    <option value="XTTS">XTTS</option>
                    <option value="Moss-TTS">Moss-TTS</option>
                    <option value="F5-TTS">F5-TTS</option>
                    <option value="Fish-Speech">Fish-Speech</option>
                    <option value="Qwen-TTS">Qwen-TTS</option>
                    <option value="Melo-TTS">Melo-TTS</option>
                    <option value="ChatTTS">ChatTTS</option>
                    <option value="CosyVoice">CosyVoice</option>
                    <option value="OpenVoice">OpenVoice</option>
                </select>
                
                <div class="field-label">Voz Padrão</div>
                <select id="elevenVoice" class="input-field" style="width:100%; margin-bottom: 15px;">
                    <option value="narrador_ref">Narrador Padrão (XTTS)</option>
                    <option value="roxingo_ref">Roxingo (XTTS)</option>
                    <option value="rafael_descargas">Rafael (Descargas)</option>
                    <option value="female_clean_ref">Feminina Clean</option>
                    <option value="custom">Upload/Outra (Selecione abaixo)</option>
                </select>
                
                <div class="field-label">Ou: Áudio de Referência (Substitui padrão)</div>
                <div class="file-input-wrap">
                    <label for="elevenRefAudio" class="file-label">📂 Escolher arquivo</label>
                    <input type="file" id="elevenRefAudio" accept="audio/*" onchange="document.getElementById('elevenRefFileName').innerText = this.files[0] ? this.files[0].name : 'Nenhum arquivo selecionado'; document.getElementById('elevenVoice').value='custom';">
                    <span class="file-name" id="elevenRefFileName">Nenhum arquivo selecionado</span>
                </div>
                
                <div class="field-label" style="margin-top:15px;">Texto para Falar</div>
                <textarea id="elevenText" class="input-field" rows="4" style="width:100%; resize:vertical;">Olá, este é o laboratório de testes do Apollo.</textarea>
                
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
"""

eleven_lab_js = """
// ----------------------------------------------------
// APOLLO ELEVEN LAB - FRONTEND LOGIC
// ----------------------------------------------------
async function generateElevenVoice() {
    const model = document.getElementById('elevenModel').value;
    const text = document.getElementById('elevenText').value;
    const voiceSelect = document.getElementById('elevenVoice').value;
    const refFile = document.getElementById('elevenRefAudio').files[0];
    const temp = document.getElementById('elevenTemp').value;
    const speed = document.getElementById('elevenSpeed').value;
    
    const status = document.getElementById('elevenStatus');
    const resultBox = document.getElementById('elevenResultBox');
    const player = document.getElementById('elevenAudioPlayer');
    const btn = document.getElementById('btnElevenGenerate');
    
    if (!text.trim()) { alert('Digite um texto!'); return; }
    
    btn.disabled = true;
    status.className = 'log-box info';
    status.textContent = '⏳ Preparando requisição e convertendo vozes...';
    resultBox.style.display = 'none';
    
    let base64Audio = null;
    let voiceName = null;
    
    try {
        if (refFile) {
            // Converte arquivo upado
            base64Audio = await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result.split(',')[1]);
                reader.onerror = error => reject(error);
                reader.readAsDataURL(refFile);
            });
        } else if (voiceSelect !== 'custom') {
            voiceName = voiceSelect;
        } else {
            // Nenhum arquivo e custom? Falta ref.
        }
        
        status.textContent = `🚀 Chamando backend para o modelo ${model} na Conta 10...`;
        
        const payload = {
            model: model,
            text: text,
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
        
        status.className = 'log-box success';
        status.textContent = `✅ Áudio gerado com sucesso via ${model}!`;
        
        player.src = url;
        resultBox.style.display = 'block';
        player.play();
        
    } catch (err) {
        console.error(err);
        status.className = 'log-box error';
        status.textContent = '❌ Erro: ' + err.message;
    } finally {
        btn.disabled = false;
    }
}
"""

# Insert HTML inside <div id="tab-audio"> before the closing </div> of that tab.
# We look for the transcriptionResult section to safely anchor it.
anchor = '📋 Copiar Texto</button>\n            </div>'
if anchor in content and "Apollo Eleven Lab" not in content:
    content = content.replace(anchor, anchor + "\n" + eleven_lab_html)

# Insert JS before </script>
js_anchor = '</script>'
if js_anchor in content and "generateElevenVoice" not in content:
    # find the last occurrence
    idx = content.rfind(js_anchor)
    content = content[:idx] + eleven_lab_js + "\n" + content[idx:]

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("Done inserting HTML & JS in modal_ai_studio.html")
