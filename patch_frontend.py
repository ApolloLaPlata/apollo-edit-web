import re

with open('public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add the engine dropdown
new_html = '''<div class="panel-header">🎙️ SÍNTESE DE VOZ E CLONAGEM</div>
                
                <div class="form-group">
                    <div class="field-label">Motor TTS (Engine)</div>
                    <select class="input-dark" id="voiceEngineSelect" style="width:100%; padding:10px; border-radius:8px; background:#0d0d15; color:var(--text); border:1px solid var(--border); margin-bottom:15px;">
                        <option value="qwen">Qwen TTS (Instrucional / Melhor Atuação)</option>
                        <option value="f5-tts" selected>F5-TTS (Zero-Shot Cloning Rápido)</option>
                        <option value="moss">MOSS-TTS 8B (Clonagem Alta Qualidade)</option>
                        <option value="xtts">XTTS v2 (Clonagem Rápida Padrão)</option>
                        <option value="kokoro">Kokoro (Vozes Embutidas English/Multi)</option>
                    </select>
                </div>
                
                <div class="form-group">'''

html = html.replace('<div class="panel-header">🎙️ SÍNTESE DE VOZ E CLONAGEM</div>\n                \n                <div class="form-group">', new_html)

# Add engine to FormData
js_old = '''const voiceId = document.getElementById('voiceIdSelect').value;
            const fileInput = document.getElementById('voiceRefFile');
            
            const formData = new FormData();
            formData.append("text", text);
            if (voiceId) formData.append("voice_id", voiceId);'''

js_new = '''const voiceId = document.getElementById('voiceIdSelect').value;
            const fileInput = document.getElementById('voiceRefFile');
            const engineId = document.getElementById('voiceEngineSelect').value;
            
            const formData = new FormData();
            formData.append("text", text);
            formData.append("engine", engineId);
            if (voiceId) formData.append("voice_id", voiceId);'''

html = html.replace(js_old, js_new)

with open('public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
    
print("Frontend patched!")
