# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/f5_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = r'''            # Converter para bytes WAV
            out_io = io.BytesIO\(\)
            sf.write\(out_io, wav, samplerate=sr, format='WAV'\)
            return out_io.getvalue\(\)'''

new_block = r'''            # Salvar como WAV temporário e converter direto para MP3 na nuvem via FFmpeg
            import subprocess
            wav_path = tempfile.mktemp(suffix=".wav")
            mp3_path = tempfile.mktemp(suffix=".mp3")
            sf.write(wav_path, wav, samplerate=sr, format='WAV')
            
            # O ffmpeg já foi instalado no image do Modal via apt_install
            subprocess.run(
                ['ffmpeg', '-y', '-i', wav_path, '-f', 'mp3', '-b:a', '64k', mp3_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            with open(mp3_path, 'rb') as f_mp3:
                mp3_bytes = f_mp3.read()
                
            os.remove(wav_path)
            os.remove(mp3_path)
            
            return mp3_bytes'''

text = re.sub(old_block, new_block, text)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patch em f5_engine.py aplicado!")
