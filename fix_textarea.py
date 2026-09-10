import re

html_path = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\modal_ai_studio.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Vamos injetar a textarea de volta no lugar certo!
target = '<div class="field-label">Letra da Música (Opcional)</div>'
injection = target + '\n                    <textarea id="musicLyrics" placeholder="[Verse 1]\\nAcordei cedo pra vencer..."></textarea>\n                </div>'

html = html.replace(target, injection)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
with open('E:\\\\MEUS PROGRAMAS\\\\APOLLO_EDIT_WEB\\\\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
