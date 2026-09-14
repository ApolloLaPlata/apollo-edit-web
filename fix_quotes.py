import re
with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

bad = '<button onclick="forceDownloadFile(${fileUrlAbs}, musica_.mp3)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">Baixar</button>'
good = "<button onclick=\"forceDownloadFile('', 'musica_.mp3')\" class=\"btn btn-primary\" style=\"white-space: nowrap; height: fit-content;\">Baixar</button>"
html = html.replace(bad, good)

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Done")
