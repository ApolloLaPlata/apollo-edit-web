import re
with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the broken one first
html = html.replace('<button onclick="forceDownloadFile(, musica_.mp3)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">Baixar</button>', '')

# Now replace it correctly
old_broken = '<button onclick="forceDownloadFile(, musica_.mp3)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">Baixar</button>'
correct = '<button onclick="forceDownloadFile(`${fileUrlAbs}`, `musica_${index}.mp3`)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">Baixar</button>'
html = html.replace(old_broken, correct)

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
