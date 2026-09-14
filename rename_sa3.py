with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<option value="sa3">Stable Audio 3 (Melhor para Efeitos Sonoros e Sound Design)</option>', '<option value="sa3">Stable Audio 3 Medium (Melhor para Efeitos Sonoros e Sound Design)</option>')

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
