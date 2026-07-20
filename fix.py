import os
path = rE:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\modal_ai_studio.html
with open(path, r, encoding=utf-8) as f:
    content = f.read()
content = content.replace(for (const line of lines) {, for (let line of lines) {)
content = content.replace(if (!line.trim()) continue;, line = line.trim();
 if (!line) continue;)
content = content.replace(} else if (data.type === result) {, } else if (data.type === result || data.status === success) {)
with open(path, w, encoding=utf-8) as f:
    f.write(content)
print(Done)
