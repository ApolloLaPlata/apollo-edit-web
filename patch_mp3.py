import sys

file_path = "/home/ubuntu/apollo_edit/servidor_web.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """                                    try:
                                        with open(filepath, "wb") as af:
                                            af.write(audio_bytes)
                                        print(f"[Modal Proxy] Audio salvo na Oracle: {filename}")
                                        data.pop("audio_base64", None)
                                        data["audio_url"] = f"https://www.apolloedit.com.br/media/{filename}"
                                    except Exception as ex:"""

new_block = """                                    try:
                                        with open(filepath, "wb") as af:
                                            af.write(audio_bytes)
                                        print(f"[Modal Proxy] Audio salvo na Oracle: {filename}")
                                        
                                        import asyncio
                                        mp3_filename = filename.replace(".wav", ".mp3")
                                        mp3_filepath = f"/home/ubuntu/apollo_edit/media/{mp3_filename}"
                                        try:
                                            proc = await asyncio.create_subprocess_exec(
                                                'ffmpeg', '-y', '-i', filepath, '-q:a', '2', mp3_filepath,
                                                stdout=asyncio.subprocess.DEVNULL,
                                                stderr=asyncio.subprocess.DEVNULL
                                            )
                                            await proc.communicate()
                                            data["audio_mp3_url"] = f"https://www.apolloedit.com.br/media/{mp3_filename}"
                                        except Exception as e_mp3:
                                            print(f"[Modal Proxy] Erro MP3: {e_mp3}")
                                            
                                        data.pop("audio_base64", None)
                                        data["audio_url"] = f"https://www.apolloedit.com.br/media/{filename}"
                                    except Exception as ex:"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCH APLICADO COM SUCESSO!")
else:
    print("ERRO: Bloco antigo nao encontrado.")
