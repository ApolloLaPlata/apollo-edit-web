import re

paths = ['public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. We replace toggleMusicUI()
    new_toggle = """function toggleMusicUI() {
            const execMode = document.querySelector('input[name="musicExecMode"]:checked').value;
            const style = document.getElementById('musicStyle').value;
            const durationMode = document.getElementById('musicDurationMode').value;
            
            // Single vs Batch Areas
            if (execMode === 'single') {
                document.getElementById('musicSingleArea').style.display = 'block';
                document.getElementById('musicBatchArea').style.display = 'none';
                document.getElementById('musicSingleLyricsContainer').style.display = (style === 'vocal') ? 'block' : 'none';
            } else {
                document.getElementById('musicSingleArea').style.display = 'none';
                document.getElementById('musicBatchArea').style.display = 'block';
                document.getElementById('musicBatchLyricsContainer').style.display = (style === 'vocal') ? 'block' : 'none';
            }
            
            const durationWrapper = document.getElementById('musicDurationModeWrapper');
            const fixedArea = document.getElementById('musicDurationFixedArea');
            const randomArea = document.getElementById('musicDurationRandomArea');
            const autoArea = document.getElementById('musicDurationAutoArea');
            
            if (style === 'vocal') {
                if (durationWrapper) durationWrapper.style.display = 'none';
                if (fixedArea) fixedArea.style.display = 'none';
                if (randomArea) randomArea.style.display = 'none';
                if (autoArea) autoArea.style.display = 'none';
            } else {
                if (durationWrapper) durationWrapper.style.display = 'block';
                if (fixedArea) fixedArea.style.display = (durationMode === 'fixed') ? 'block' : 'none';
                if (randomArea) randomArea.style.display = (durationMode === 'random') ? 'flex' : 'none';
                if (autoArea) autoArea.style.display = (durationMode === 'auto') ? 'flex' : 'none';
            }
        }"""
    
    html = re.sub(r'function toggleMusicUI\(\) \{[\s\S]*?(?=function stopMusicMaster)', new_toggle + "\n\n          ", html)

    # 2. We fix generateMusicMaster and downloadAllBatchFiles so they force 'auto' for vocal
    # For downloadAllBatchFiles:
    html = html.replace(
        "const durationMode = document.getElementById('musicDurationMode').value;",
        "let durationMode = document.getElementById('musicDurationMode').value;\n            if (style === 'vocal') durationMode = 'auto';"
    )
    
    # Same for generateMusicMaster
    # Wait, let's just make sure we replace ALL `const durationMode` to `let durationMode`
    # and add the override.
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

print("Patched toggles!")
