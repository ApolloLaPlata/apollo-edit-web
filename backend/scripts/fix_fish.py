import re

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\engines\fish_engine.py"
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

old_logic = """        data = await request.json()
        text = data.get("text", "")
        ref_audio_base64 = data.get("ref_audio_base64", None)
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        reference_audio_bytes = None
        if ref_audio_base64:
            import base64
            reference_audio_bytes = base64.b64decode(ref_audio_base64)
            
        tts_service = FishTTSEngine()
        audio_bytes = tts_service.generate_voice.remote(text, reference_audio_bytes=reference_audio_bytes)"""

new_logic = """        data = await request.json()
        text = data.get("text", "")
        ref_audio_base64 = data.get("ref_audio_base64", None)
        ref_text = data.get("ref_text", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        reference_audio_bytes = None
        if ref_audio_base64:
            import base64
            reference_audio_bytes = base64.b64decode(ref_audio_base64)
            
        tts_service = FishTTSEngine()
        audio_bytes = tts_service.generate_voice.remote(text, reference_audio_bytes=reference_audio_bytes, reference_text=ref_text)"""

content = content.replace(old_logic, new_logic)

with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated fish_engine.py")
