with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('max="120"', 'max="300"')

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
