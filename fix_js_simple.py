paths = ['public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']
for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    bad = 'forceDownloadFile(${fileUrlAbs}, musica_.mp3)'
    good = "forceDownloadFile('', 'musica_.mp3')"
    
    html = html.replace(bad, good)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
print("Replaced!")
