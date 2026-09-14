import re
paths = ['public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']
for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # The bad pattern has backticks inside the onclick
    # We want to replace it with single quotes
    bad = r'<button onclick="forceDownloadFile\(\$\{fileUrlAbs\},\s*musica_\$\{index\}\.mp3\)"'
    good = r"<button onclick=\"forceDownloadFile('', 'musica_.mp3')\""
    
    html = re.sub(bad, good, html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

print("Replaced!")
