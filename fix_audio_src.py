import sys
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "document.getElementById('musicPlayer').src = data.audio_url;",
    "document.getElementById('musicPlayer').src = data.audio_base64 ? 'data:audio/wav;base64,' + data.audio_base64 : data.audio_url;"
)

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
