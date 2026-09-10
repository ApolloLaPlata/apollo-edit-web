with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("modal.Image.debian_slim()", "modal.Image.debian_slim().apt_install('ffmpeg')")

route_code = """
class ConvertMp3Request(BaseModel):
    audio_base64: str

@web_app.post("/api/studio/modal/convert_mp3")
async def convert_mp3_route(req: ConvertMp3Request, request: Request):
    if request.headers.get("x-apollo-lock") != "apollo-beta-key-2026":
        return {"error": "Unauthorized"}
    try:
        import base64
        import subprocess
        import os
        import uuid
        
        wav_data = base64.b64decode(req.audio_base64)
        unique_id = uuid.uuid4().hex
        wav_path = f"/tmp/{unique_id}.wav"
        mp3_path = f"/tmp/{unique_id}.mp3"
        
        with open(wav_path, "wb") as f:
            f.write(wav_data)
            
        subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", mp3_path], check=True, capture_output=True)
        
        with open(mp3_path, "rb") as f:
            mp3_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        try:
            os.remove(wav_path)
            os.remove(mp3_path)
        except:
            pass
        
        return {"status": "success", "audio_base64": mp3_b64}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

class AudioLabRequest"""

code = code.replace("class AudioLabRequest", route_code)

with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py", "w", encoding="utf-8") as f:
    f.write(code)
