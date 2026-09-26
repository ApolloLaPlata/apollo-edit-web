import os
import requests
import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/tts", tags=["TTS Proxy"])

CENTRAL_API_URL = "https://api.v5apollo.com"

@router.get("/personagens")
def proxy_personagens():
    try:
        # Puxa da API Central
        resp = requests.get(f"{CENTRAL_API_URL}/api/tts/personagens", timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {"success": False, "error": f"Central API Error: {resp.status_code}"}
    except Exception as e:
        # Fallback de mock pra nǜo quebrar a UI
        return {
            "success": True,
            "personagens": [
                {"id": "rafael_multimodal", "nome": "Rafael (Multimodal)", "engine": "xtts"},
                {"id": "pt_br_femea", "nome": "Ana (Ultra)", "engine": "eleven"}
            ]
        }

@router.post("/gerar")
async def proxy_gerar(request: Request):
    try:
        payload = await request.json()
        
        # Envia para a API Central
        resp = requests.post(f"{CENTRAL_API_URL}/api/tts/gerar", json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("audio_base64"):
                import base64
                import uuid
                audio_data = base64.b64decode(data["audio_base64"])
                filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
                filepath = os.path.join("media", filename)
                os.makedirs("media", exist_ok=True)
                with open(filepath, "wb") as f:
                    f.write(audio_data)
                
                # Retorna o arquivo salvo no VPS para a UI poder colocar na Timeline!
                return {"success": True, "audio_url": f"/media/{filename}"}
            return data
        return {"success": False, "error": f"Central API Error: {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
