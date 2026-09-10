import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

metadata_logic = '''
            audio_data = base64.b64decode(audio_b64)
            
            # Smart Naming & Metadata Extraction
            import re
            
            title = "Faixa Gerada"
            artist = "Apollo AI Studio"
            lyrics_block = ""
            
            # Tentar extrair um título da letra ou do estilo
            if "Lyrics:" in prompt:
                # É vocal
                parts = prompt.split("Lyrics:")
                style_part = parts[0].strip()
                lyrics_block = parts[1].strip()
                
                # Pegar a primeira linha válida da letra como título
                lyrics_lines = [l.strip() for l in lyrics_block.split('\\n') if l.strip() and not l.strip().startswith('[')]
                if lyrics_lines:
                    title = lyrics_lines[0][:30].title()
                else:
                    title = style_part[:30].title()
            else:
                title = prompt[:30].title()
            
            # Limpar caracteres inválidos para nome de arquivo
            safe_title = re.sub(r'[^a-zA-Z0-9 _-]', '', title).strip().replace(' ', '_')
            if not safe_title: safe_title = "track"
            
            filename = f"{safe_title}_{uuid.uuid4().hex[:4]}.mp3"
            
            os.makedirs("temp", exist_ok=True)
            filepath = os.path.join("temp", filename)
            with open(filepath, "wb") as f:
                f.write(audio_data)
                
            # Injetar Metadados MP3 usando Mutagen
            try:
                from mutagen.id3 import ID3, TIT2, TPE1, TALB, USLT, ID3NoHeaderError
                try:
                    audio_tags = ID3(filepath)
                except ID3NoHeaderError:
                    audio_tags = ID3()
                
                audio_tags.add(TIT2(encoding=3, text=title))
                audio_tags.add(TPE1(encoding=3, text=artist))
                audio_tags.add(TALB(encoding=3, text="Dark Trap Radio - Lote AI"))
                if lyrics_block:
                    audio_tags.add(USLT(encoding=3, lang='por', desc='Letra', text=lyrics_block))
                    
                audio_tags.save(filepath)
                print(f"[Audio Generator] Metadados ID3 injetados com sucesso! Título: {title}")
            except Exception as meta_err:
                print(f"[Audio Generator] Aviso: Falha ao injetar metadados ID3: {meta_err}")
                
            print(f"[Audio Generator] Salvo em {filepath}")
            return {"success": True, "file_url": f"/temp/{filename}"}
'''

code = re.sub(
    r'audio_data = base64\.b64decode\(audio_b64\).*?return \{"success": True, "file_url": f"/temp/\{filename\}"\}',
    metadata_logic.strip(),
    code,
    flags=re.DOTALL
)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)
