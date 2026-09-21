import sys

with open('servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_save_code = """            os.makedirs("temp", exist_ok=True)
            filepath = os.path.join("temp", filename)
            with open(filepath, "wb") as f:
                f.write(audio_data)
                
            # Injetar Metadados MP3 usando Mutagen"""

new_save_code = """            os.makedirs("temp", exist_ok=True)
            filepath = os.path.join("temp", filename)
            
            temp_raw = filepath + ".raw"
            with open(temp_raw, "wb") as f:
                f.write(audio_data)
                
            import subprocess
            subprocess.run(["ffmpeg", "-y", "-i", temp_raw, "-b:a", "192k", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import os
            if os.path.exists(temp_raw):
                os.remove(temp_raw)
                
            # Injetar Metadados MP3 usando Mutagen"""

if old_save_code in code:
    code = code.replace(old_save_code, new_save_code)
    with open('servidor_web.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Sucesso!")
else:
    print("String nao encontrada.")
