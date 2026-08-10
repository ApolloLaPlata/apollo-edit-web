# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/xtts_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = r'''            # Converter para bytes WAV
            out_io = io.BytesIO()
            # O XTTSv2 usa 24000 de samplerate geralmente
            sf.write(out_io, wav, samplerate=24000, format='WAV')
            return out_io.getvalue()'''

new_block = r'''            # CONVERSÃO OPUS 100% EM MEMÓRIA (Nativo para o Chat)
            import subprocess
            out_io = io.BytesIO()
            # O XTTSv2 usa 24000 de samplerate geralmente
            sf.write(out_io, wav, samplerate=24000, format='WAV')
            wav_bytes = out_io.getvalue()
            
            proc = subprocess.Popen(
                ['ffmpeg', '-i', 'pipe:0', '-c:a', 'libopus', '-b:a', '32k', '-vbr', 'on', '-f', 'ogg', 'pipe:1'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            opus_bytes, _ = proc.communicate(input=wav_bytes)
            
            return opus_bytes'''

text = re.sub(old_block, new_block, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("xtts_engine.py atualizado com Opus RAM!")
