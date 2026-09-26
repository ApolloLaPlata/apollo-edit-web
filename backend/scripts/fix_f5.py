import re

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\engines\f5_engine.py"
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

old_logic = """        data = await request.json()
        text = data.get("text", "")
        ref_b64 = data.get("ref_audio_base64", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        ref_bytes = base64.b64decode(ref_b64) if ref_b64 else None
            
        tts_service = F5TTSEngine()
        audio_bytes = tts_service.generate_voice.remote(text, ref_bytes)"""

new_logic = """        data = await request.json()
        text = data.get("text", "")
        ref_b64 = data.get("ref_audio_base64", "")
        ref_text = data.get("ref_text", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        ref_bytes = base64.b64decode(ref_b64) if ref_b64 else None
            
        tts_service = F5TTSEngine()
        audio_bytes = tts_service.generate_voice.remote(text, ref_bytes, ref_text)"""

content = content.replace(old_logic, new_logic)

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated f5_engine.py")
