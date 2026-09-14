import sys

files = ["public/modal_ai_studio.html", "frontend/modal_ai_studio.html", "web_ui/modal_ai_studio.html", "modal_ai_studio.html"]

script_to_inject = """
            const musicModelSelect = document.getElementById('musicModel');
            if (musicModelSelect) {
                musicModelSelect.addEventListener('change', () => {
                    const styleSelect = document.getElementById('musicStyle');
                    if (musicModelSelect.value === 'sa3') {
                        // Bloquear vocais no Stable Audio
                        styleSelect.value = 'instrumental';
                        for (let option of styleSelect.options) {
                            if (option.value === 'vocal') option.disabled = true;
                        }
                        toggleMusicUI();
                    } else {
                        // Desbloquear
                        for (let option of styleSelect.options) {
                            option.disabled = false;
                        }
                    }
                });
            }
"""

for file in files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        
        if "musicModelSelect.addEventListener" not in text:
            # Encontrar o window.addEventListener('DOMContentLoaded', () => {
            target = "window.addEventListener('DOMContentLoaded', () => {"
            text = text.replace(target, target + script_to_inject)
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Patched {file} for SA3.")
    except Exception as e:
        print(e)
