from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse
import os
import time

router = APIRouter(prefix="/api/audio", tags=["Audio Lab"])

@router.post("/lab_test")
async def audio_lab_test(
    model: str = Form(...),
    prompt: str = Form(...),
    lyrics: str = Form(None),
    duration: int = Form(30),
    ref_audio: UploadFile = File(None)
):
    # 1. Salvar áudio de referência (se existir)
    ref_path = None
    if ref_audio:
        os.makedirs("temp_audio", exist_ok=True)
        ref_path = f"temp_audio/ref_{int(time.time())}_{ref_audio.filename}"
        with open(ref_path, "wb") as f:
            content = await ref_audio.read()
            f.write(content)
            
    # 2. Lógica de Roteamento Individual para Testes
    try:
        if model == "sa3":
            return JSONResponse({"success": True, "message": "SA3 Recebido!", "audio_url": "/sua_url_falsa.wav", "debug_prompt": prompt})
        elif model == "minimax":
            return JSONResponse({"success": True, "message": "MiniMax Recebido!", "audio_url": "/sua_url_falsa.wav", "debug_prompt": prompt})
        elif model == "ace-step":
            return JSONResponse({"success": True, "message": "ACE-Step Recebido!", "audio_url": "/sua_url_falsa.wav", "debug_prompt": prompt, "lyrics": lyrics})
        else:
            return JSONResponse({"success": False, "error": "Modelo desconhecido."})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})
