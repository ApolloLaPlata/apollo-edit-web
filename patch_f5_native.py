# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/f5_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = r'''            # Salvar como WAV e converter para Opus \(OGG\) na nuvem - Máxima Otimização de Peso
            import subprocess
            wav_path = tempfile.mktemp\(suffix="\.wav"\)
            opus_path = tempfile.mktemp\(suffix="\.ogg"\)
            sf.write\(wav_path, wav, samplerate=sr, format='WAV'\)
            
            # Opus a 32kbps é incrivelmente leve para voz \(cerca de metade do MP3 64k\)
            subprocess.run\(
                \['ffmpeg', '-y', '-i', wav_path, '-c:a', 'libopus', '-b:a', '32k', '-f', 'ogg', opus_path\],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            \)
            
            with open\(opus_path, 'rb'\) as f_opus:
                opus_bytes = f_opus.read\(\)
                
            os.remove\(wav_path\)
            os.remove\(opus_path\)
            
            return opus_bytes'''

new_block = r'''            # CONVERSÃO DIRETA EM MEMÓRIA (Numpy Array -> OPUS)
            # Sem passar por WAV, para otimizar processamento na Nuvem!
            import subprocess
            import numpy as np
            
            # 1. Converte o array matemático (float) da IA direto para PCM 16-bit bruto
            pcm_bytes = (wav * 32767).astype(np.int16).tobytes()
            
            # 2. Injeta o PCM direto no encoder Opus (em RAM, sem tocar o disco)
            proc = subprocess.Popen(
                ['ffmpeg', '-f', 's16le', '-ar', str(sr), '-ac', '1', '-i', 'pipe:0', 
                 '-c:a', 'libopus', '-b:a', '32k', '-f', 'ogg', 'pipe:1'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            opus_bytes, _ = proc.communicate(input=pcm_bytes)
            
            return opus_bytes'''

text = re.sub(old_block, new_block, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch Opus Nativo aplicado em f5_engine.py!")
