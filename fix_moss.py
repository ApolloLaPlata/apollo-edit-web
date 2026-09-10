import os
import json

with open('tts_manager.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_moss = False
for line in lines:
    if 'url = "https://historiasde7dias--apollo-api-moss-tts.modal.run"' in line:
        in_moss = True
        
    if in_moss:
        if 'elif modelo_tts == 3:' in line:
            in_moss = False
            # inject moss payload
            new_lines.append('''            url = "https://historiasde7dias--apollo-api-moss-tts.modal.run"
            import time, requests, base64
            print(f"🚀 Enviando requisição direta para Modal Moss-TTS ({url})...")
            
            try:
                with open(audio_ref, "rb") as f:
                    audio_base64 = base64.b64encode(f.read()).decode("utf-8")
                    
                payload = {
                    "text": text,
                    "reference_audio_base64": audio_base64,
                    "language": "Portuguese"
                }
                
                max_retries = 3
                for attempt in range(max_retries):
                    print(f"📡 [Tentativa {attempt+1}/{max_retries}] Conectando ao Moss-TTS Modal...")
                    t0 = time.time()
                    response = requests.post(url, json=payload, timeout=600)
                    
                    if response.status_code == 200:
                        audio_res = response.content
                        if audio_res:
                            with open(output_path, "wb") as f:
                                f.write(audio_res)
                            print(f"✅ [Moss-TTS] Áudio recebido e salvo com sucesso em {time.time() - t0:.2f}s!")
                            return True
                    else:
                        print(f"⚠️ [Moss-TTS] Falha na requisição (HTTP {response.status_code}): {response.text[:200]}")
                        if attempt < max_retries - 1:
                            time.sleep(3)
                        else:
                            return False
            except Exception as e:
                print(f"❌ Erro ao rotear para Moss TTS: {e}")
                return False\n''')
            new_lines.append(line)
    else:
        new_lines.append(line)

with open('tts_manager.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
