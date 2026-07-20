import os
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.tts_manager import TTSManager

logger = logging.getLogger("RoutesTTS")
router = APIRouter(prefix="/api/v1/tts", tags=["TTS"])

tts_jobs = {}

# Em ambiente de produção o config_manager precisa ser passado ou inicializado globalmente.
# Como estamos apenas instanciando as rotas para validação, vamos assumir None ou config vazio.
try:
    from backend.main import CONFIG
except ImportError:
    CONFIG = {}
    
class DummyConfigManager:
    def get(self, key, default=None):
        return CONFIG.get(key, default)
        
    def get_voicemaker_config(self, key):
        return None
        
    def get_gemini_config(self, key):
        return None
        
    def get_api_config(self, group, key=None):
        return None
        
tts_engine = TTSManager(DummyConfigManager())

class TTSRequest(BaseModel):
    user_id: str
    text: str
    engine: str = "edge"
    voice: str = "pt-BR-AntonioNeural"
    output_name: str = "tts_output.mp3"

def process_tts_job(job_id: str, req: TTSRequest):
    logger.info(f"[{job_id}] Iniciando processamento de TTS: {req.text[:30]}...")
    tts_jobs[job_id]["status"] = "processing"
    
    try:
        output_path = f"temp_outputs/{job_id}_{req.output_name}"
        
        # Chama a API do TTS Manager
        res = tts_engine.gerar_audio_sync(
            texto=req.text,
            caminho_arquivo=output_path,
            engine=req.engine,
            voz=req.voice
        )
        
        if res:
            tts_jobs[job_id]["status"] = "completed"
            tts_jobs[job_id]["result_audio"] = output_path
            logger.info(f"[{job_id}] TTS concluído. Áudio salvo em {output_path}")
        else:
            tts_jobs[job_id]["status"] = "failed"
            tts_jobs[job_id]["error"] = "Erro interno no TTSManager"
            
    except Exception as e:
        logger.error(f"[{job_id}] Erro ao gerar TTS: {e}")
        tts_jobs[job_id]["status"] = "failed"
        tts_jobs[job_id]["error"] = str(e)

@router.post("/generate")
async def generate_tts(request: TTSRequest, background_tasks: BackgroundTasks):
    job_id = f"tts_{uuid.uuid4().hex[:8]}"
    tts_jobs[job_id] = {
        "status": "queued",
        "req": request.model_dump(),
        "job_id": job_id
    }
    
    background_tasks.add_task(process_tts_job, job_id, request)
    
    return {
        "status": "success",
        "job_id": job_id,
        "message": "Tarefa de geração de áudio TTS iniciada localmente."
    }

@router.get("/status/{job_id}")
async def get_tts_status(job_id: str):
    job = tts_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return job


