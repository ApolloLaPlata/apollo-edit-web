import sys

with open('modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('id="musicRefAudio" accept="audio/*"', 'id="musicRefAudio" accept="audio/*,video/*,.mpeg,.mp4,.ogg,.m4a,.webm,.wav,.mp3"')

with open('modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
