import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'audio_chunk = await f5\.generate_voice\.remote\.aio\(chunk, ref_bytes\)\s+await websocket\.send_bytes\(audio_chunk\)\s+except Exception as f5_err:',
    r'audio_chunk = await f5.generate_voice.remote.aio(chunk, ref_bytes)\n                              except Exception as f5_err:',
    text
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Servidor_web fix applied!")
