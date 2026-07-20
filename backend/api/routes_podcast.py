import os
import uuid
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.podcast_engine import PodcastGenerator

logger = logging.getLogger("RoutesPodcast")
router = APIRouter(prefix="/api/v1/podcast", tags=["Podcast"])

podcast_jobs = {}
podcast_engine = PodcastGenerator()

class PodcastRequest(BaseModel):
    user_id: str
    script_text: str
    output_name: str = "podcast_output.mp3"
    add_bgm: bool = False
    bgm_path: Optional[str] = None
    voice_map: Optional[Dict[str, str]] = None  # { "Hospedeiro": "Lúcio", "Convidado": "Marina" }

def process_podcast_job(job_id: str, req: PodcastRequest):
    logger.info(f"[{job_id}] Iniciando processamento do podcast")
    podcast_jobs[job_id]["status"] = "processing"
    
    try:
        output_path = f"temp_outputs/{job_id}_{req.output_name}"
        
        # Aqui o PodcastGenerator vai interpretar o texto, separar por falas, 
        # chamar o TTS pra cada fala, e unir tudo com FFmpeg
        # (Depende de como o gerador_podcast.py implementa, mas em geral é o método generate ou build)
        
        # Simulando ou adaptando à chamada real do PodcastGenerator
        script_tmp = f'temp_outputs/{job_id}_script.txt'
        with open(script_tmp, 'w', encoding='utf-8') as f:
            f.write(req.script_text)
        final_audio = podcast_engine.generate_podcast(script_tmp, modes={'smart_pacing': True}, normalize_audio=True, gerar_mapa_cores=False)
            
        podcast_jobs[job_id]["status"] = "completed"
        podcast_jobs[job_id]["result_audio"] = final_audio
        logger.info(f"[{job_id}] Podcast concluído. Áudio salvo em {final_audio}")
        
    except Exception as e:
        logger.error(f"[{job_id}] Erro ao gerar podcast: {e}")
        podcast_jobs[job_id]["status"] = "failed"
        podcast_jobs[job_id]["error"] = str(e)

@router.post("/generate")
async def generate_podcast(request: PodcastRequest, background_tasks: BackgroundTasks):
    job_id = f"pod_{uuid.uuid4().hex[:8]}"
    podcast_jobs[job_id] = {
        "status": "queued",
        "req": request.model_dump(),
        "job_id": job_id
    }
    
    background_tasks.add_task(process_podcast_job, job_id, request)
    
    return {
        "status": "success",
        "job_id": job_id,
        "message": "Tarefa de geração de podcast iniciada localmente."
    }

@router.get("/status/{job_id}")
async def get_podcast_status(job_id: str):
    job = podcast_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return job

