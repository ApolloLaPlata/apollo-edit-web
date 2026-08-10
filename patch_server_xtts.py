# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/servidor_web.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Substituir importação e instanciação
text = text.replace(
    'from backend.cloud_tools.engines.f5_engine import F5TTSEngine',
    'from backend.cloud_tools.engines.xtts_engine import XttsEngine'
)
text = text.replace(
    'f5 = F5TTSEngine()',
    'xtts = XttsEngine()'
)

# Substituir a chamada e tratamento de erro
text = text.replace(
    'audio_chunk = await f5.generate_voice.remote.aio(chunk, ref_bytes)',
    'audio_chunk = await xtts.generate_voice.remote.aio(chunk, ref_bytes)'
)
text = text.replace(
    'except Exception as f5_err:',
    'except Exception as xtts_err:'
)
text = text.replace(
    'print(f"[WS] F5TTS Modal falhou: {f5_err}")',
    'print(f"[WS] XTTS Modal falhou: {xtts_err}")'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("servidor_web.py atualizado para XTTS!")
