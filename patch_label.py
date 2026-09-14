import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Wrap the label and select in a div
html = html.replace('<div class="field-label">Modo de Duração</div>', '<div id="musicDurationModeWrapper"><div class="field-label">Modo de Duração</div>')
html = html.replace('<option value="random">Aleatório (Entre Min e Max)</option>\n                      \n                  </select>', '<option value="random">Aleatório (Entre Min e Max)</option>\n                      \n                  </select></div>')

# In toggleMusicUI(), hide the wrapper instead of just the select
html = html.replace("const durationSelect = document.getElementById('musicDurationMode');", "const durationSelect = document.getElementById('musicDurationModeWrapper');")

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
