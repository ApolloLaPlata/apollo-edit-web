import sys
import re

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Change the url to explicitly hit the Oracle IP to avoid Vercel timeouts
if "'/api/studio/modal/generate/audio_lab'" in text:
    text = text.replace(
        "const url = '/api/studio/modal/generate/audio_lab';",
        "const url = 'http://163.176.135.59/api/studio/modal/generate/audio_lab';"
    )

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
