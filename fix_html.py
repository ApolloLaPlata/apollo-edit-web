import os
path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\modal_ai_studio.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('if (!line.trim()) continue;', 'const trimmedLine = line.trim();\n                    if (!trimmedLine) continue;')
content = content.replace('if (!line.startsWith(\'{\')) {', 'if (!trimmedLine.startsWith(\'{\')) {')
content = content.replace('const data = JSON.parse(line);', 'const data = JSON.parse(trimmedLine);')
content = content.replace('} else if (data.type === "result") {', '} else if (data.type === "result" || data.status === "success") {')
content = content.replace('currentImageData = data.image_base64;', 'currentImageData = data.image_base64 || data.audio_base64 || data.video_url || "";')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
