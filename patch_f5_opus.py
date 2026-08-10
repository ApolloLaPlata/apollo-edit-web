# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/f5_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = r'''            # Salvar como WAV temporário e converter direto para MP3 na nuvem via FFmpeg
            import subprocess
            wav_path = tempfile.mktemp\(suffix="\.wav"\)
            mp3_path = tempfile.mktemp\(suffix="\.mp3"\)
            sf.write\(wav_path, wav, samplerate=sr, format='WAV'\)
            
            # O ffmpeg já foi instalado no image do Modal via apt_install
            subprocess.run\(
                \['ffmpeg', '-y', '-i', wav_path, '-f', 'mp3', '-b:a', '64k', mp3_path\],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            \)
            
            with open\(mp3_path, 'rb'\) as f_mp3:
                mp3_bytes = f_mp3.read\(\)
                
            os.remove\(wav_path\)
            os.remove\(mp3_path\)
            
            return mp3_bytes'''

new_block = r'''            # Salvar como WAV e converter para Opus (OGG) na nuvem - Máxima Otimização de Peso
            import subprocess
            wav_path = tempfile.mktemp(suffix=".wav")
            opus_path = tempfile.mktemp(suffix=".ogg")
            sf.write(wav_path, wav, samplerate=sr, format='WAV')
            
            # Opus a 32kbps é incrivelmente leve para voz (cerca de metade do MP3 64k)
            subprocess.run(
                ['ffmpeg', '-y', '-i', wav_path, '-c:a', 'libopus', '-b:a', '32k', '-f', 'ogg', opus_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            with open(opus_path, 'rb') as f_opus:
                opus_bytes = f_opus.read()
                
            os.remove(wav_path)
            os.remove(opus_path)
            
            return opus_bytes'''

text = re.sub(old_block, new_block, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch Opus aplicado em f5_engine.py!")
