import sys

files = ["public/modal_ai_studio.html", "frontend/modal_ai_studio.html", "web_ui/modal_ai_studio.html", "modal_ai_studio.html"]

upload_html = """
                <div class="field-label" id="refAudioLabel">Ã udio de ReferÃªncia (Voz/Estilo) - Opcional</div>
                <input type="file" id="musicRefAudio" accept="audio/*" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px; margin-bottom: 15px;">
"""

for file in files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        
        if "musicRefAudio" not in text:
            target = '<button id="musicCancelBtn" class="btn btn-secondary"'
            if target in text:
                text = text.replace(target, upload_html + "\n" + target)
                with open(file, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Patched HTML in {file}")
            else:
                print("Target button not found.")
    except Exception as e:
        print(f"Error {file}: {e}")
