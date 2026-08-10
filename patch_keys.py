# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix proxy key
text = re.sub(
    r'backend_key = chat_cfg\.get\("api_key", ""\)',
    r'''api_keys = chat_cfg.get("api_keys", [])
        if api_keys and isinstance(api_keys, list):
            import random
            backend_key = random.choice(api_keys)
        else:
            backend_key = chat_cfg.get("api_key", "")''',
    text
)

# Fix /api/chat/send used_api_key
text = re.sub(
    r'used_api_key = api_key if api_key else chat_cfg\.get\("api_key", ""\)',
    r'''api_keys = chat_cfg.get("api_keys", [])
        if api_key:
            used_api_key = api_key
        elif api_keys and isinstance(api_keys, list):
            import random
            used_api_key = random.choice(api_keys)
        else:
            used_api_key = chat_cfg.get("api_key", "")''',
    text
)

# Fix WHATSAPP DIRECT API KEY
text = re.sub(
    r'api_key = chat_cfg\.get\("api_key", ""\)',
    r'''api_keys = chat_cfg.get("api_keys", [])
        if api_keys and isinstance(api_keys, list):
            import random
            api_key = random.choice(api_keys)
        else:
            api_key = chat_cfg.get("api_key", "")''',
    text
)

# Fix F5TTS fallback
f5_old = r'except Exception as f5_err:\s+print\(f"\[WS\] F5TTS gerou erro \(Modal pode não estar rodando\): \{f5_err\}"\)'
f5_new = r'''except Exception as f5_err:
                                print(f"[WS] F5TTS gerou erro (Modal pode nao estar rodando). Fallback edge-tts: {f5_err}")
                                import subprocess
                                import tempfile
                                import os
                                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                                    temp_name = f.name
                                try:
                                    subprocess.run(["edge-tts", "--text", chunk, "--write-media", temp_name, "--voice", "pt-BR-AntonioNeural"], creationflags=subprocess.CREATE_NO_WINDOW)
                                    with open(temp_name, "rb") as f:
                                        audio_chunk = f.read()
                                    await websocket.send_bytes(audio_chunk)
                                except Exception as edge_err:
                                    print(f"Erro no edge-tts: {edge_err}")
                                finally:
                                    if os.path.exists(temp_name):
                                        os.remove(temp_name)'''
text = re.sub(f5_old, f5_new, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Servidor_web patch applied!")
