import os
import json

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

search_text = """    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ROTAS PARA O NARRADOR"""

replace_text = """    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ROTAS DO GERENCIADOR DE MULTI-VOZES (XTTS + KOKORO) =====
@app.get("/api/voice/catalog")
def get_voice_catalog():
    import os
    import glob
    catalog = [
        {"id": "kokoro_pf_dora", "name": "Kokoro - Dora (Feminino)", "engine": "kokoro", "type": "standard"},
        {"id": "kokoro_pm_lucas", "name": "Kokoro - Lucas (Masculino)", "engine": "kokoro", "type": "standard"}
    ]
    xtts_dir = os.path.join(BASE_DIR, "backend", "voices", "xtts")
    if os.path.exists(xtts_dir):
        for wav_file in glob.glob(os.path.join(xtts_dir, "*.wav")):
            base_name = os.path.splitext(os.path.basename(wav_file))[0]
            clean_name = base_name.replace("_ref", "").capitalize()
            catalog.append({"id": f"xtts_{base_name}", "name": f"XTTS Clone - {clean_name}", "engine": "xtts", "type": "zero-shot"})
    return {"success": True, "catalog": catalog}

import urllib.request
import base64
from fastapi import Request

@app.get("/api/tts/test")
@app.post("/api/voice/generate")
async def voice_generate(request: Request):
    text = ""
    voice_id = ""
    if request.method == "GET":
        text = request.query_params.get("text", "")
        voice_id = request.query_params.get("voice", "kokoro_pf_dora")
    else:
        data = await request.json()
        text = data.get("text", "")
        voice_id = data.get("voice_id", "kokoro_pf_dora")
        
    if not text:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "Texto não fornecido"}, status_code=400)
        
    MODAL_USER = "filosofiadocodigo"
    
    if voice_id.startswith("kokoro_"):
        kokoro_voice = voice_id.replace("kokoro_", "")
        url = f"https://{MODAL_USER}--apollo-api-tts.modal.run/"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")
        import json
        payload = json.dumps({"text": text, "voice": kokoro_voice}).encode('utf-8')
        try:
            with urllib.request.urlopen(req, data=payload) as response:
                audio_bytes = response.read()
                from fastapi.responses import Response
                return Response(content=audio_bytes, media_type="audio/wav")
        except Exception as e:
            from fastapi.responses import JSONResponse
            return JSONResponse({"error": f"Erro Kokoro Modal: {str(e)}"}, status_code=500)
            
    elif voice_id.startswith("xtts_"):
        wav_name = voice_id.replace("xtts_", "")
        xtts_dir = os.path.join(BASE_DIR, "backend", "voices", "xtts")
        wav_path = os.path.join(xtts_dir, f"{wav_name}.wav")
        
        if not os.path.exists(wav_path):
            from fastapi.responses import JSONResponse
            return JSONResponse({"error": f"Áudio de referência não encontrado: {wav_path}"}, status_code=404)
            
        with open(wav_path, "rb") as f:
            ref_bytes = f.read()
            ref_b64 = base64.b64encode(ref_bytes).decode('utf-8')
            
        url = f"https://{MODAL_USER}--apollo-api-xtts.modal.run/"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")
        import json
        payload = json.dumps({"text": text, "ref_audio_base64": ref_b64}).encode('utf-8')
        
        try:
            with urllib.request.urlopen(req, data=payload) as response:
                audio_bytes = response.read()
                from fastapi.responses import Response
                return Response(content=audio_bytes, media_type="audio/wav")
        except Exception as e:
            from fastapi.responses import JSONResponse
            return JSONResponse({"error": f"Erro XTTS Modal: {str(e)}"}, status_code=500)
            
    from fastapi.responses import JSONResponse
    return JSONResponse({"error": "Engine desconhecida"}, status_code=400)

# ===== ROTAS PARA O NARRADOR"""

if search_text in content:
    content = content.replace(search_text, replace_text)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sucesso!")
else:
    print("Falhou ao achar string alvo")
