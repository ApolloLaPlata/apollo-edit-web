from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response, JSONResponse
import httpx
import base64
import os

router = APIRouter(prefix="/api/tts_v2", tags=["TTS_V2"])

MODAL_WORKSPACE = "sitesviniciusmiranda"

ENGINES = {
    "XTTS": "xtts",
    "F5-TTS": "f5-tts",
    "Moss-TTS": "moss-tts",
    "Qwen-TTS": "qwen-tts",
    "CosyVoice": "cosyvoice",
    "Kokoro": "kokoro",
    "Fish-Speech": "fish-speech",
    "OpenVoice": "openvoice"
}

@router.get("/engines")
async def get_engines():
    return JSONResponse(content={"success": True, "engines": list(ENGINES.keys())})

@router.post("/generate")
async def generate_tts(request: Request):
    try:
        data = await request.json()
        engine_name = data.get("engine", "Qwen-TTS")
        text = data.get("text", "")
        reference_audio_base64 = data.get("reference_audio_base64", "")
        reference_text = data.get("reference_text", "")
        instruct_text = data.get("instruct_text", "")
        
        if engine_name not in ENGINES:
            return JSONResponse({"success": False, "error": "Invalid engine name"}, status_code=400)
            
        endpoint_suffix = ENGINES[engine_name]
        url = f"https://{MODAL_WORKSPACE}--apollo-api-{endpoint_suffix}.modal.run"
        
        # Se nao tiver audio de referencia, envia um vazio ou um default falso para nao quebrar
        if not reference_audio_base64:
            import wave, io, struct
            fake_wav = io.BytesIO()
            with wave.open(fake_wav, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(24000)
                for _ in range(24000):
                    wav.writeframes(struct.pack('h', 0))
            reference_audio_base64 = base64.b64encode(fake_wav.getvalue()).decode("utf-8")
        
        payload = {
            "text": text,
            "reference_audio_base64": reference_audio_base64,
            "ref_audio_base64": reference_audio_base64,  # Para retrocompatibilidade de alguns scripts
            "reference_text": reference_text,
            "ref_text": reference_text,
            "prompt_text": reference_text,
            "instruct_text": instruct_text
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code == 200:
                return Response(content=res.content, media_type="audio/wav")
            else:
                return JSONResponse({"success": False, "error": f"Modal Error: {res.text}"}, status_code=500)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
