import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\pocket_app.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

search = '''    this.ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        const data = JSON.parse(event.data);
        this.handleServerEvent(data);
      }
    };'''

replace = '''    this.ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        const data = JSON.parse(event.data);
        this.handleServerEvent(data);
      } else if (event.data instanceof Blob) {
        // Play audio chunk from backend directly (Chat Ao Vivo)
        const url = URL.createObjectURL(event.data);
        const audio = new Audio(url);
        audio.play().catch(e => console.error("Audio play error:", e));
      }
    };'''

if search in content:
    content = content.replace(search, replace)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sucesso!")
else:
    print("Falha ao localizar string no JS")
