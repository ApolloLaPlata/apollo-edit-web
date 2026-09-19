from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, Response
import httpx
import base64
import os
from typing import Optional

router = APIRouter(prefix="/api/voice", tags=["Voice TTS"])

MODAL_WORKSPACE = "sitesviniciusmiranda"

# Catalog mapping
CATALOG = {
    "kokoro": [
        {"id": "pf_dora", "name": "Dora (Feminina)"},
        {"id": "pf_julia", "name": "Julia (Feminina)"},
        {"id": "pf_leticia", "name": "Letícia (Feminina)"},
        {"id": "pm_alex", "name": "Alex (Masculino)"},
        {"id": "pm_lucas", "name": "Lucas (Masculino)"}
    ],
    "qwen": [
        {"id": "narrador_ref", "name": "Narrador Padrão (Local)"},
        {"id": "rafael_descargas", "name": "Rafael Descargas (Local)"},
        {"id": "female_clean_ref", "name": "Feminina Clean (Local)"}
    ],
    "f5-tts": [
        {"id": "narrador_ref", "name": "Narrador Padrão (Local)"},
        {"id": "rafael_descargas", "name": "Rafael Descargas (Local)"},
        {"id": "female_clean_ref", "name": "Feminina Clean (Local)"}
    ],
    "moss": [
        {"id": "narrador_ref", "name": "Narrador Padrão (Local)"},
        {"id": "female_clean_ref", "name": "Feminina Clean (Local)"}
    ],
    "xtts": [
        {"id": "narrador_ref", "name": "Narrador Padrão (Local)"},
        {"id": "roxingo_ref", "name": "Roxingo (Local)"},
        {"id": "female_clean_ref", "name": "Feminina Clean (Local)"}
    ]
}

# Local Reference Map
LOCAL_VOICE_MAP = {
    "narrador_ref": r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\voices\xtts\narrador_ref.wav",
    "roxingo_ref": r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\voices\xtts\roxingo_ref.wav",
    "rafael_descargas": r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\testes_tts\rafael_descargas.wav",
    "female_clean_ref": r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\testes_tts\female_clean_ref.wav"
}

# Modal Endpoints Mapping
ENDPOINTS = {
    "qwen": f"https://{MODAL_WORKSPACE}--apollo-api-qwen-tts.modal.run",
    "f5-tts": f"https://{MODAL_WORKSPACE}--apollo-api-f5-tts.modal.run",
    "moss": f"https://{MODAL_WORKSPACE}--apollo-api-moss-tts.modal.run",
    "xtts": f"https://{MODAL_WORKSPACE}--apollo-api-xtts.modal.run",
    "kokoro": f"https://{MODAL_WORKSPACE}--apollo-api-tts.modal.run",
}

@router.get("/catalog")
async def get_catalog(engine: str = "f5-tts"):
    catalog = CATALOG.get(engine, [])
    return {"success": True, "catalog": catalog}

@router.post("/studio_generate")
async def studio_generate(
    text: str = Form(...),
    engine: str = Form(...),
    voice_id: Optional[str] = Form(None),
    voice_file: Optional[UploadFile] = File(None)
):
    url = ENDPOINTS.get(engine)
    if not url:
        return JSONResponse({"success": False, "error": f"Engine {engine} não suportada ou URL inválida."}, status_code=400)

    base64_audio = None

    # Handle Uploaded File
    if voice_file:
        file_bytes = await voice_file.read()
        base64_audio = base64.b64encode(file_bytes).decode("utf-8")
    
    # Handle Local Cloned Voice selection
    elif voice_id and voice_id in LOCAL_VOICE_MAP:
        file_path = LOCAL_VOICE_MAP[voice_id]
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                base64_audio = base64.b64encode(f.read()).decode("utf-8")

    # Build payload
    req_payload = {
        "text": text,
        "temperature": 0.7,
        "speed": 1.0,
        "language": "pt",
        "return_raw_wav": True
    }

    # Handle Native Voice IDs (e.g., kokoro: pf_dora)
    if not base64_audio and voice_id and voice_id not in LOCAL_VOICE_MAP:
        req_payload["voice"] = voice_id
        req_payload["voice_name"] = voice_id

    # If cloning is needed but not provided
    if base64_audio:
        req_payload["ref_audio_base64"] = base64_audio
        req_payload["reference_audio_base64"] = base64_audio

    try:
        async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
            res = await client.post(url, json=req_payload)
            if res.status_code != 200:
                return JSONResponse({"success": False, "error": f"Erro Modal: {res.text}"}, status_code=500)
            
            return Response(content=res.content, media_type="audio/wav")
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
