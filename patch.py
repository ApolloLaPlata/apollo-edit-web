# coding=utf-8
import sys, os

with open('tts_manager.py', 'r', encoding='utf-8') as f:
    code = f.read()

xtts_code = """
        elif modelo_tts == 6:
            print(f"[XTTS] Roteando para XTTS na NUVEM MODAL (Modelo 6) para o personagem {character_name}")
            
            audio_ref = personagem.get("audio_ref_moss", "")
            if not audio_ref or not os.path.exists(audio_ref):
                print(f"[Erro] Áudio de referência não configurado ou ausente para {character_name}.")
                return False
                
            import time
            import requests
            import base64
            
            start_time = time.time()
            try:
                print("[XTTS] Conectando ao Roteador Modal...")
                
                with open(audio_ref, "rb") as f:
                    ref_b64 = base64.b64encode(f.read()).decode('utf-8')
                    
                payload = {
                    "engine": "xtts",
                    "text": text,
                    "reference_audio_base64": ref_b64,
                    "language": "Portuguese"
                }
                
                url = "https://apolloeditweb--apollo-render-router-apollo-api.modal.run/generate/tts"
                response = requests.post(url, json=payload, timeout=600, stream=True)
                
                if response.status_code == 200:
                    import json
                    audio_res = None
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8').strip()
                            if not line_str: continue
                            try:
                                data = json.loads(line_str)
                                if data.get("status") == "success" and "audio_base64" in data:
                                    audio_res = base64.b64decode(data["audio_base64"])
                                    break
                                elif data.get("status") == "error":
                                    print(f"❌ [XTTS] Erro do Servidor: {data.get('message')}")
                                    return False
                            except json.JSONDecodeError:
                                pass
                    
                    if audio_res:
                        with open(output_path, "wb") as f:
                            f.write(audio_res)
                        print(f"✅ [XTTS] Clone perfeito gerado em {time.time() - start_time:.2f}s!")
                        return True
                    else:
                        print("❌ [XTTS] Erro: Resposta incompleta do servidor.")
                        return False
                else:
                    print(f"❌ [XTTS] Erro HTTP {response.status_code}: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ Erro ao rotear para XTTS: {e}")
                return False
"""

# Try to find the else block
search_str = "        else:\n            print(f\"â Œ Modelo TTS roteado desconhecido"

if search_str in code:
    code = code.replace(search_str, xtts_code + "\n" + search_str)
    with open('tts_manager.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Patched!")
else:
    print("Could not find the target string. Using fallback...")
    search_str2 = "        else:\n            print(f\"❌ Modelo TTS roteado desconhecido"
    if search_str2 in code:
        code = code.replace(search_str2, xtts_code + "\n" + search_str2)
        with open('tts_manager.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("Patched with fallback!")
    else:
        print("Fallback also failed. Check file manually.")
