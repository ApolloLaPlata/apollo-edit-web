import re

with open('servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the studio_voice_generate function
new_func = '''@app.post("/api/voice/studio_generate")
async def studio_voice_generate(text: str = Form(...), engine: str = Form("f5-tts"), voice_id: str = Form(None), voice_file: UploadFile = File(None)):
    import base64
    import urllib.request
    import json
    import os
    
    MODAL_USER = "apollolaplata"
    
    if engine == "qwen":
        url = f"https://{MODAL_USER}--apollo-api-qwen-tts.modal.run/"
    elif engine == "moss":
        url = f"https://{MODAL_USER}--apollo-api-moss-tts.modal.run/"
    elif engine == "xtts":
        url = f"https://{MODAL_USER}--apollo-api-xtts.modal.run/"
    elif engine == "kokoro":
        url = f"https://{MODAL_USER}--apollo-api-tts.modal.run/"
    else:
        url = f"https://{MODAL_USER}--apollo-api-f5-tts.modal.run/"
    
    ref_bytes = b""
    if voice_file:
        ref_bytes = await voice_file.read()
    elif voice_id:
        v_name = voice_id.replace("f5_", "").replace("kokoro_", "")
        if not v_name.endswith(".wav"): v_name += ".wav"
        default_path = os.path.join(BASE_DIR, "backend", "voices", "xtts", v_name)
        if os.path.exists(default_path):
            with open(default_path, "rb") as f:
                ref_bytes = f.read()
                
    ref_b64 = base64.b64encode(ref_bytes).decode('utf-8') if ref_bytes else ""
    
    # Formatação de payload específica por engine (Modal APIs)
    payload_dict = {"text": text}
    
    if engine == "f5-tts":
        payload_dict["ref_audio_base64"] = ref_b64
    elif engine == "moss":
        payload_dict["reference_audio_base64"] = ref_b64
    elif engine == "qwen":
        payload_dict["reference_audio_base64"] = ref_b64
        payload_dict["reference_text"] = " " # Qwen precisa de ref_text
    elif engine == "xtts":
        payload_dict["reference_audio"] = ref_b64
    elif engine == "kokoro":
        payload_dict["voice"] = voice_id.replace("kokoro_", "") if voice_id else "af_heart"
        
    payload = json.dumps(payload_dict).encode('utf-8')
    
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=payload) as response:
            audio_bytes = response.read()
            from fastapi.responses import Response
            return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": f"Erro {engine} Modal Studio: {str(e)}"}, status_code=500)'''

pattern = re.compile(r'@app\.post\("/api/voice/studio_generate"\)\nasync def studio_voice_generate.*?return JSONResponse\(\{"error": "Engine desconhecida"\}, status_code=400\)', re.DOTALL)
if pattern.search(code):
    code = pattern.sub(new_func, code)
    with open('servidor_web.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("servidor_web.py patched!")
else:
    print("Pattern not found in servidor_web.py!")
