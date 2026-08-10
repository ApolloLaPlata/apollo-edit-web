# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/f5_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = r'''            # CONVERSÃO DIRETA EM MEMÓRIA \(Numpy Array -> OPUS\)
            # Sem passar por WAV, para otimizar processamento na Nuvem!
            import subprocess
            import numpy as np
            
            # 1\. Converte o array matemático \(float\) da IA direto para PCM 16-bit bruto
            pcm_bytes = \(wav \* 32767\)\.astype\(np\.int16\)\.tobytes\(\)
            
            # 2\. Injeta o PCM direto no encoder Opus \(em RAM, sem tocar o disco\)
            proc = subprocess\.Popen\(
                \['ffmpeg', '-f', 's16le', '-ar', str\(sr\), '-ac', '1', '-i', 'pipe:0', 
                 '-c:a', 'libopus', '-b:a', '32k', '-f', 'ogg', 'pipe:1'\],
                stdin=subprocess\.PIPE,
                stdout=subprocess\.PIPE,
                stderr=subprocess\.DEVNULL
            \)
            opus_bytes, _ = proc\.communicate\(input=pcm_bytes\)
            
            return opus_bytes'''

new_block = r'''            # CONVERSÃO OPUS 100% EM MEMÓRIA
            # Usa o soundfile para garantir a conversão matemática correta do numpy array para WAV em memória
            import subprocess
            import io
            import soundfile as sf
            
            wav_io = io.BytesIO()
            sf.write(wav_io, wav, samplerate=sr, format='WAV')
            wav_bytes = wav_io.getvalue()
            
            # Injeta o WAV da memória direto no FFmpeg para virar Opus (sem tocar o disco)
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

print("Patch Opus RAM seguro aplicado em f5_engine.py!")
