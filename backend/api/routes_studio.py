import os
import json
import httpx
import uuid
import asyncio
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Response
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
import hashlib

global_modal_semaphore = asyncio.Semaphore(2)

router = APIRouter(prefix="/api/studio/modal", tags=["Studio Modal Proxy"])

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cloud_tools", "cloud_accounts_db.json"))

JOBS = {}

def get_active_modal_account():
    if not os.path.exists(DB_FILE):
        return None
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            accounts = json.load(f)
        except:
            return None
    for acc in accounts:
        if acc.get("provider") == "modal" and acc.get("is_active"):
            return acc
    return None

async def process_modal_job(job_id: str, method: str, url: str, headers: dict, body: bytes):
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
            try:
                content = response.json()
            except:
                content = response.text
                
            JOBS[job_id] = {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "content": content
            }
        except Exception as e:
            JOBS[job_id] = {
                "status": "error",
                "status_code": 500,
                "content": {"error": str(e)}
            }

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(status_code=200, content=JOBS[job_id])

@router.api_route("/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_to_modal(path: str, request: Request, background_tasks: BackgroundTasks):
    if request.method == "OPTIONS":
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    # --- INTERNAL LOCK (BOT PROTECTION) ---
    expected_lock = os.environ.get("APOLLO_SECRET_LOCK", "apollo-beta-key-2026")
    client_lock = request.headers.get("x-apollo-lock")
    if client_lock != expected_lock:
        raise HTTPException(status_code=401, detail="Unauthorized access. Bot protection is active.")
    # --------------------------------------
    
    # Dual-routing system for Modalities
    workspace = "sitesviniciusmiranda" # fallback
    
    remote_path = path
    if path == "generate_image":
        remote_path = "generate/image"
        workspace = "canalobservadoreconomico" # Conta 7
    elif path == "generate_video":
        remote_path = "generate/video"
        workspace = "canalobservadoreconomico" # Conta 7
    elif path == "generate_universal":
        remote_path = "generate/universal"
        workspace = "canalobservadoreconomico" # Conta 7
    elif path == "generate_tts":
        remote_path = "generate/tts"
        workspace = "sitesviniciusmiranda" # Conta 10
        
    modal_url = f"https://{workspace}--apollo-render-router-apollo-api.modal.run/{remote_path}"
    print(f"[PROXY DEBUG] Routing to: {modal_url}", flush=True)
    
    headers = {}
    if acc.get("proxy_secret"):
        headers["Authorization"] = f"Bearer {acc.get('proxy_secret')}"
    
    if "content-type" in request.headers:
        headers["Content-Type"] = request.headers["content-type"]
            
    body = await request.body()
    
    # --- QWEN MULTI-PASS INTERCEPT REMOVED BY USER REQUEST ---

    # Execucao com Streaming para repassar heartbeats e evitar 504 no Nginx
    print(f"[PROXY DEBUG] [RATE LIMIT] Aguardando liberacao na fila da Modal (Max 2 simultaneos)...", flush=True)
    async with global_modal_semaphore:
        print(f"[PROXY DEBUG] [RATE LIMIT] Fila liberada! Enviando requisicao para a Modal.", flush=True)
        client = httpx.AsyncClient(timeout=300.0)
        try:
            req = client.build_request(
                method=request.method,
                url=modal_url,
                headers=headers,
                content=body
            )
            response = await client.send(req, stream=True)
            
            async def stream_gen():
                try:
                    async for chunk in response.aiter_raw():
                        yield chunk
                finally:
                    await response.aclose()
                    await client.aclose()
                    
            return StreamingResponse(
                stream_gen(),
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json")
            )
        except Exception as e:
            await client.aclose()
            raise HTTPException(status_code=500, detail=str(e))











import base64
from pydantic import BaseModel
from typing import Optional
import httpx
from fastapi.responses import Response

class ElevenLabRequest(BaseModel):
    model: str
    text: str
    instruct: Optional[str] = None
    ref_text: Optional[str] = None
    temperature: float = 0.7
    speed: float = 1.0
    voice_name: Optional[str] = None
    ref_audio_base64: Optional[str] = None

@router.post("/eleven_lab")
async def generate_eleven_lab(payload: ElevenLabRequest):
    try:
        import os
        workspace = os.getenv("MODAL_WORKSPACE_TTS", "sitesviniciusmiranda")
        endpoints = {
            "Qwen-TTS": f"https://{workspace}--apollo-api-qwen-tts.modal.run",
            "XTTS": f"https://{workspace}--apollo-api-xtts.modal.run",
            "Moss-TTS": f"https://{workspace}--apollo-api-moss-tts.modal.run",
            "F5-TTS": f"https://{workspace}--apollo-api-f5-tts.modal.run",
            "Fish-Speech": f"https://{workspace}--apollo-api-fish-tts.modal.run",
            "Fish-TTS-Basic": f"https://{workspace}--apollo-api-fish-tts-basic.modal.run",
            "Kokoro-TTS": f"https://{workspace}--apollo-api-tts.modal.run",
            "Melo-TTS": f"https://{workspace}--apollo-api-melo.modal.run",
            "ChatTTS": f"https://{workspace}--apollo-api-chattts.modal.run",
            "CosyVoice": f"https://{workspace}--apollo-api-cosyvoice.modal.run",
            "OpenVoice": f"https://{workspace}--apollo-api-openvoice.modal.run"
        }
        
        url = endpoints.get(payload.model)
        if not url:
            raise HTTPException(status_code=400, detail=f"Modelo {payload.model} nÃ£o configurado.")

        # Resolver voz local se nao foi enviado base64
        base64_audio = payload.ref_audio_base64
        if not base64_audio and payload.voice_name and payload.voice_name != "custom":
            # Procura nos diretorios padrÃ£o
            voice_map = {
                "narrador_ref": r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\voices\xtts\narrador_ref.wav",
                "roxingo_ref": r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\voices\xtts\roxingo_ref.wav",
                "rafael_descargas": r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\testes_tts\rafael_descargas.wav",
                "female_clean_ref": r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\testes_tts\female_clean_ref.wav"
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
        
        # O Qwen TTS e possivelmente outros usam "instruct" para emocao/prompt de interpretacao
        if payload.instruct:
            req_payload["instruct"] = payload.instruct
            req_payload["prompt"] = payload.instruct  # Compatibilidade com outros que esperam prompt
            
        if payload.ref_text:
            req_payload["ref_text"] = payload.ref_text
            req_payload["reference_text"] = payload.ref_text
        
        if base64_audio:
            req_payload["ref_audio_base64"] = base64_audio
            req_payload["reference_audio_base64"] = base64_audio

        print(f"[ElevenLab Backend] Chamando Modal Webhook: {url}")
        
        async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
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



