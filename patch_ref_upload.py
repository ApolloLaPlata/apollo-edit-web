import sys

files = ["public/modal_ai_studio.html", "frontend/modal_ai_studio.html", "web_ui/modal_ai_studio.html", "modal_ai_studio.html"]

upload_html = """
                <div class="field-label">Ãudio de ReferÃªncia (Opcional - Voz/Estilo)</div>
                <input type="file" id="musicRefAudio" accept="audio/*" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
"""

for file in files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        
        if "musicRefAudio" not in text:
            # Inserir depois do musicDurationAutoArea
            target = '<div id="musicDurationAutoArea" style="display:none; gap:10px; margin-bottom:15px;">\n                      <div class="field-label" style="line-height:35px; color:var(--text-dim);">Tamanho gerado automaticamente conforme a letra</div>\n                  </div>'
            if target in text:
                text = text.replace(target, target + "\n" + upload_html)
            else:
                print(f"Target not found in {file}")
                
            # Atualizar JS para capturar Base64
            js_target = "const engine = document.getElementById('musicModel').value;"
            js_new = js_target + """
            
            // Ler arquivo de referÃªncia se existir
            let refAudioB64 = "";
            const refFile = document.getElementById('musicRefAudio')?.files[0];
            if (refFile) {
                refAudioB64 = await new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onload = (e) => resolve(e.target.result.split(',')[1]);
                    reader.readAsDataURL(refFile);
                });
            }
"""
            text = text.replace(js_target, js_new)
            
            # Adicionar no fetch payload
            payload_target = "body: JSON.stringify({ prompt: p, engine, lyrics: lyrics[i] || \"\", duration: finalDuration })"
            payload_new = "body: JSON.stringify({ prompt: p, engine, lyrics: lyrics[i] || \"\", duration: finalDuration, reference_audio_b64: refAudioB64 })"
            text = text.replace(payload_target, payload_new)
            
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Patched HTML {file}")
    except Exception as e:
        print(f"Error {file}: {e}")
