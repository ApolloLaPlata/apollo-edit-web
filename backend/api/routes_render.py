from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any
import os

from backend.engines.video_engine import AsyncVideoEngine
from backend.engines.audio_engine import AsyncAudioEngine
from backend.engines.director_engine import AsyncDirectorEngine
from backend.router.waterfall_router import WaterfallRouter

router = APIRouter(prefix="/render", tags=["Render Engines"])

# Inicializando os motores globais (Em produção, o waterfall_router é injetado ou instanciado globalmente)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

video_engine = AsyncVideoEngine(root_path=ROOT_DIR)
audio_engine = AsyncAudioEngine()
# director_engine será inicializado quando necessário caso use injecao de dependencia

class RenderJobRequest(BaseModel):
    timeline_data: Dict[str, Any]

@router.post("/start_video")
async def start_video_render(request: RenderJobRequest):
    """
    Inicia o render da timeline em background via FFmpeg (VideoEngine).
    """
    try:
        job_id = await video_engine.start_render(request.timeline_data)
        return {"status": "success", "job_id": job_id, "message": "Renderização de vídeo iniciada no background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status_video/{job_id}")
async def get_video_status(job_id: str):
    """
    Retorna o progresso do render do vídeo.
    """
    status = video_engine.get_status(job_id)
    if status["state"] == "not_found":
        raise HTTPException(status_code=404, detail="Job ID não encontrado.")
    return {"job_id": job_id, "status": status}

class AudioJobRequest(BaseModel):
    audio_path: str
    noise_level: str = "-40dB"

@router.post("/clean_audio")
async def clean_audio(request: AudioJobRequest):
    """
    Remove silêncios do áudio de forma assíncrona usando FFmpeg.
    """
    # Para rotas muito longas, deveria retornar um Job ID, mas para o exemplo usamos await
    # Na arquitetura real de produção, áudio pesado também ganha job_id
    try:
        if not os.path.exists(request.audio_path):
            raise HTTPException(status_code=404, detail="Arquivo de áudio não encontrado.")
            
        out_path = await audio_engine.remover_silencio_ffmpeg(request.audio_path, noise=request.noise_level)
        return {"status": "success", "processed_file": out_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DirectorRequest(BaseModel):
    script_text: str

@router.post("/analyze_script")
async def analyze_script(request: DirectorRequest):
    """
    Aciona o Director Engine (LLM) para extrair palavras-chave do roteiro.
    """
    try:
        router_instance = WaterfallRouter()
        director = AsyncDirectorEngine(router=router_instance)
        
        analysis = await director.analyze_script(request.script_text)
        return {"status": "success", "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
