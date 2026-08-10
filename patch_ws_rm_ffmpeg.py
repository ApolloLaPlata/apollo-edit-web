# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = r'''if 'audio_chunk' in locals\(\) and audio_chunk:
                                  # Converte WAV \(audio_chunk\) para MP3 na memÃ³ria usando ffmpeg para otimizar velocidade no front
                                  import subprocess
                                  try:
                                      proc = subprocess\.Popen\(
                                          \['ffmpeg', '-i', 'pipe:0', '-f', 'mp3', '-b:a', '64k', 'pipe:1'\],
                                          stdin=subprocess\.PIPE,
                                          stdout=subprocess\.PIPE,
                                          stderr=subprocess\.DEVNULL,
                                          creationflags=subprocess\.CREATE_NO_WINDOW
                                      \)
                                      mp3_chunk, _ = proc\.communicate\(input=audio_chunk\)
                                      await websocket\.send_bytes\(mp3_chunk\)
                                  except Exception as conv_err:
                                      print\(f"Falha ao converter MP3, enviando WAV: \{conv_err\}"\)
                                      await websocket\.send_bytes\(audio_chunk\)'''

new_block = r'''if 'audio_chunk' in locals() and audio_chunk:
                                  # O Modal já devolveu o buffer em MP3, enviamos direto!
                                  await websocket.send_bytes(audio_chunk)'''

text = re.sub(old_block, new_block, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch em servidor_web.py aplicado para enviar MP3 direto!")
