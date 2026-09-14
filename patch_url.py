import re

with open('apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\"file_url\": f\"/media/audio_lab/{filename}\"', '\"file_url\": f\"https://www.apolloedit.com/media/audio_lab/{filename}\"')

with open('apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(content)
