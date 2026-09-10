import re
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"http://163.176.135.59/api/studio/modal/ping"', '"/api/studio/modal/ping"')
text = text.replace('"http://163.176.135.59/api/studio/modal/generate_image"', '"/api/studio/modal/generate_image"')
text = text.replace('"http://163.176.135.59/api/studio/modal/transcribe"', '"/api/studio/modal/transcribe"')

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
