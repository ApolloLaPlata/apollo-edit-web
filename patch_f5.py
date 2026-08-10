# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix F5 initialization
text = re.sub(
    r'if engine == \'f5\':\s+from backend\.cloud_tools\.engines\.f5_engine import F5TTSEngine\s+f5 = F5TTSEngine\(\)',
    r'''if engine == 'f5':
                import modal
                f5_cls = modal.Cls.from_name("apollo-render-router", "F5TTSEngine")
                f5 = f5_cls()''',
    text
)

# Fix F5 usage and add MP3 conversion
f5_old = r'''except Exception as f5_err:
                                print\(f"\[WS\] F5TTS gerou erro \(Modal pode nao estar rodando\)\. Fallback edge-tts: \{f5_err\}"\)
                                import subprocess
                                import tempfile
                                import os
                                with tempfile\.NamedTemporaryFile\(suffix="\.mp3", delete=False\) as f:
                                    temp_name = f\.name
                                try:
                                    subprocess\.run\(\["edge-tts", "--text", chunk, "--write-media", temp_name, "--voice", "pt-BR-AntonioNeural"\], creationflags=subprocess\.CREATE_NO_WINDOW\)
                                    with open\(temp_name, "rb"\) as f:
                                        audio_chunk = f\.read\(\)
                                    await websocket\.send_bytes\(audio_chunk\)
                                except Exception as edge_err:
                                    print\(f"Erro no edge-tts: \{edge_err\}"\)
                                finally:
                                    if os\.path\.exists\(temp_name\):
                                        os\.remove\(temp_name\)'''

f5_new = r'''except Exception as f5_err:
                                print(f"[WS] F5TTS Modal falhou: {f5_err}")
                            if 'audio_chunk' in locals() and audio_chunk:
                                # Converte WAV (audio_chunk) para MP3 na memÃ³ria usando ffmpeg para otimizar velocidade no front
                                import subprocess
                                try:
                                    proc = subprocess.Popen(
                                        ['ffmpeg', '-i', 'pipe:0', '-f', 'mp3', '-b:a', '64k', 'pipe:1'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL,
                                        creationflags=subprocess.CREATE_NO_WINDOW
                                    )
                                    mp3_chunk, _ = proc.communicate(input=audio_chunk)
                                    await websocket.send_bytes(mp3_chunk)
                                except Exception as conv_err:
                                    print(f"Falha ao converter MP3, enviando WAV: {conv_err}")
                                    await websocket.send_bytes(audio_chunk)'''

text = re.sub(f5_old, f5_new, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Servidor_web F5TTS e MP3 patch applied!")
