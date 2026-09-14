import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the encoding bug by using regex
html = re.sub(r'(<div class="field-label">Modo de Dura.*?</div>\s*<select id="musicDurationMode".*?Aleat.*?<\/option>\s*<\/select>)', r'<div id="musicDurationModeWrapper">\1</div>', html, flags=re.DOTALL)

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
