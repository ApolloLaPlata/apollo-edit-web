import os

FILE_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_studio.py"

endpoint_code = """
import base64
from pydantic import BaseModel
from typing import Optional
import httpx
from fastapi.responses import Response

class ElevenLabRequest(BaseModel):
    model: str
    text: str
    temperature: float = 0.7
    speed: float = 1.0
    voice_name: Optional[str] = None
    ref_audio_base64: Optional[str] = None

@router.post("/eleven_lab")
async def generate_eleven_lab(payload: ElevenLabRequest):
    try:
        endpoints = {
            "Qwen-TTS": "https://apollolaplata--apollo-api-qwen-tts.modal.run",
            "XTTS": "https://apollolaplata--apollo-api-xtts.modal.run",
            "Moss-TTS": "https://apollolaplata--apollo-api-moss-tts.modal.run",
            "F5-TTS": "https://apollolaplata--apollo-api-f5-tts.modal.run",
            "Fish-Speech": "https://apollolaplata--apollo-api-fish-tts.modal.run",
            "Melo-TTS": "https://apollolaplata--apollo-api-melo-tts.modal.run",
            "ChatTTS": "https://apollolaplata--apollo-api-chattts.modal.run",
            "CosyVoice": "https://apollolaplata--apollo-api-cosyvoice.modal.run",
            "OpenVoice": "https://apollolaplata--apollo-api-openvoice.modal.run"
        }
        
        url = endpoints.get(payload.model)
        if not url:
            raise HTTPException(status_code=400, detail=f"Modelo {payload.model} não configurado.")

        # Resolver voz local se nao foi enviado base64
        base64_audio = payload.ref_audio_base64
        if not base64_audio and payload.voice_name and payload.voice_name != "custom":
            # Procura nos diretorios padrão
            voice_map = {
                "narrador_ref": r"E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\backend\\voices\\xtts\\narrador_ref.wav",
                "roxingo_ref": r"E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\backend\\voices\\xtts\\roxingo_ref.wav",
                "rafael_descargas": r"E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas.wav",
                "female_clean_ref": r"E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\female_clean_ref.wav"
            }
            file_path = voice_map.get(payload.voice_name)
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    base64_audio = base64.b64encode(f.read()).decode("utf-8")
        
        req_payload = {
            "text": payload.text,
            "temperature": payload.temperature,
            "speed": payload.speed,
            "language": "pt",
            "return_raw_wav": True
        }
        
        if base64_audio:
            req_payload["ref_audio_base64"] = base64_audio
            req_payload["reference_audio_base64"] = base64_audio

        print(f"[ElevenLab Backend] Chamando Modal Webhook: {url}")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            res = await client.post(url, json=req_payload)
            
            if res.status_code != 200:
                print(f"[ElevenLab Backend] Erro no Webhook: {res.text}")
                raise HTTPException(status_code=res.status_code, detail=res.text)
                
            media_type = res.headers.get("content-type", "audio/wav")
            return Response(content=res.content, media_type=media_type)
            
    except Exception as e:
        import traceback
        print(f"[ElevenLab Backend] Exception: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
"""

with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

if "/eleven_lab" not in content:
    with open(FILE_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + endpoint_code)
    print("Endpoint appended!")
else:
    print("Endpoint already exists!")
