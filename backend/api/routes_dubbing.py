import os
import uuid
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.media_adjuster import MediaProcessor

logger = logging.getLogger("RoutesDubbing")
router = APIRouter(prefix="/api/v1/dubbing", tags=["Dubbing"])

dubbing_jobs = {}

class DubbingRequest(BaseModel):
    user_id: str
    media_path: str
    action: str = "adjust" # adjust, dub

def process_dubbing_job(job_id: str, req: DubbingRequest):
    logger.info(f"[{job_id}] Iniciando processo de dublagem/ajuste para {req.media_path}")
    dubbing_jobs[job_id]["status"] = "processing"
    
    try:
        if req.action == "adjust":
            processor = MediaProcessor()
            # Faria as chamadas de FFmpeg necessárias usando o serviço
            # Ex: output_path = processor.processar(...)
            output_path = f"temp_outputs/{job_id}_adjusted.mp4"
            # Simulando o sucesso por enquanto, a lógica real depende da parametrização do MediaProcessor
            dubbing_jobs[job_id]["status"] = "completed"
            dubbing_jobs[job_id]["result_media"] = output_path
        else:
            raise NotImplementedError("Ação de dublagem RVC não implementada nesta rota ainda.")
            
    except Exception as e:
        logger.error(f"[{job_id}] Erro: {e}")
        dubbing_jobs[job_id]["status"] = "failed"
        dubbing_jobs[job_id]["error"] = str(e)

@router.post("/process")
async def generate_dubbing(request: DubbingRequest, background_tasks: BackgroundTasks):
    job_id = f"dub_{uuid.uuid4().hex[:8]}"
    dubbing_jobs[job_id] = {
        "status": "queued",
        "req": request.model_dump(),
        "job_id": job_id
    }
    background_tasks.add_task(process_dubbing_job, job_id, request)
    return {
        "status": "success",
        "job_id": job_id
    }
