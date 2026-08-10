import base64
import re

html_path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/teste_audio.html'
out_path = r'C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\audio_teste.ogg'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# extrair o base64
match = re.search(r'base64,([^"]+)"', html)
if match:
    b64_data = match.group(1)
    audio_bytes = base64.b64decode(b64_data)
    with open(out_path, 'wb') as f_out:
        f_out.write(audio_bytes)
    print("Áudio OGG salvo com sucesso em:", out_path)
else:
    print("Base64 não encontrado no HTML.")
