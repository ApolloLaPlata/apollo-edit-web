import os

html_path = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\modal_ai_studio.html'
with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('Ã udio', 'Áudio')
text = text.replace('MÃºsica', 'Música')
text = text.replace('Letra da MÃºsica', 'Letra da Música')
text = text.replace('Ã udio de', 'Áudio de')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)
with open('E:\\\\MEUS PROGRAMAS\\\\APOLLO_EDIT_WEB\\\\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
