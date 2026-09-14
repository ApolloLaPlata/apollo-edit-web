import re
with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(
    r'<button onclick="forceDownloadFile\(\$\{fileUrlAbs\},\s*musica_\$\{index\}\.mp3\)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">Baixar</button>',
    r"<button onclick=\"forceDownloadFile('', 'musica_.mp3')\" class=\"btn btn-primary\" style=\"white-space: nowrap; height: fit-content;\">Baixar</button>",
    html
)

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done regex")
