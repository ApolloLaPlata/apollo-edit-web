import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Wrap Modo de Duração
# Ensure we don't double wrap
if 'id="musicDurationModeWrapper"' not in html:
    html = re.sub(
        r'(<div class="field-label">Modo de Dura.*?</div>\s*<select id="musicDurationMode".*?<\/select>)',
        r'<div id="musicDurationModeWrapper">\1</div>',
        html,
        flags=re.DOTALL
    )

# 2. toggleMusicUI hiding the wrapper and hiding random/fixed/dropdown properly for Vocal
html = html.replace(
    "const durationSelect = document.getElementById('musicDurationMode');",
    "const durationSelect = document.getElementById('musicDurationModeWrapper');"
)

# 3. Add single lyrics array loading
old_single = "prompts = [p];"
new_single = "prompts = [p];\n            lyrics = [l];"
html = html.replace(old_single, new_single)

# 4. JSON.stringify payload sending lyrics
old_json = 'body: JSON.stringify({ prompt: p, engine, duration: finalDuration })'
new_json = 'body: JSON.stringify({ prompt: p, engine, lyrics: lyrics[i] || "", duration: finalDuration })'
html = html.replace(old_json, new_json)

# 5. forceDownloadFile function
func = """
function forceDownloadFile(url, filename) {
    fetch(url)
    .then(r => r.blob())
    .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
    }).catch(e => {
        alert('Erro ao baixar: ' + e.message);
    });
}
"""
if 'function forceDownloadFile' not in html:
    html = html.replace('// --- GLOBALS & HELPERS ---', '// --- GLOBALS & HELPERS ---\n' + func)

# 6. Replace <a> with <button> for download
old_btn = '<a href="" download="musica_.mp3" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">\u2b07\ufe0f Baixar</a>'
new_btn = '<button onclick="forceDownloadFile(${fileUrlAbs}, musica_.mp3)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">Baixar</button>'
html = html.replace(old_btn, new_btn)

# Just in case the emoji differs, we can use regex
html = re.sub(
    r'<a href="\$\{fileUrlAbs\}" download="musica_\$\{index\}\.mp3" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">.*?Baixar</a>',
    r'<button onclick="forceDownloadFile(${fileUrlAbs}, musica_.mp3)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">Baixar</button>',
    html
)

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Patched correctly!")
