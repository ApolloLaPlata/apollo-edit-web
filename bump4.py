import os
for path in ['public/hub.html', 'web_ui/hub.html']:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace('modal_ai_studio.html?v=7', 'modal_ai_studio.html?v=8')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
