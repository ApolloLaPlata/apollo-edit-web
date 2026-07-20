import os
import uuid
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.subtitle_service import gerar_legendas_ass_e_queimar

logger = logging.getLogger("RoutesSubtitles")
router = APIRouter(prefix="/api/v1/subtitles", tags=["Subtitles"])

# Simula banco de dados em memória para as tarefas (jobs) de legendas
subtitle_jobs = {}

class SubtitleRequest(BaseModel):
    user_id: str
    media_path: str
    srt_path: Optional[str] = None
    engine: str = "vosk" # ou "whisper"
    font: str = "Bangers"
    size: int = 100
    theme: str = "amarelo vermelho"
    pos: str = "meio baixo"
    margin_v: int = 150
    words_per_block: int = 5
    video_format: str = "vertical"
    effect: str = "Pulo (Pop)"
    border_w: int = 3

def process_subtitle_job(job_id: str, req: SubtitleRequest):
    logger.info(f"[{job_id}] Iniciando processamento de legendas para {req.media_path}")
    subtitle_jobs[job_id]["status"] = "processing"
    
    try:
        output_path = f"temp_outputs/{job_id}_legendado.mp4"
        
        # O modelo do vosk por padrão tenta buscar no diretório ou usar um pré-configurado
        # Aqui, como estamos focados em rodar, passamos um caminho padrão ou vazio
        vosk_model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pre_edicao', 'vosk-model-small-pt-0.3')
        
        # Chama a função extraída das antigas ferramentas locais do Tkinter
        final_video = gerar_legendas_ass_e_queimar(
            media_path=req.media_path,
            srt_path=req.srt_path,
            output_path=output_path,
            vosk_model_dir=vosk_model_dir,
            engine=req.engine,
            font=req.font,
            size=req.size,
            theme=req.theme,
            pos=req.pos,
            margin_v=req.margin_v,
            words_per_block=req.words_per_block,
            video_format=req.video_format,
            effect=req.effect,
            border_w=req.border_w
        )
        
        subtitle_jobs[job_id]["status"] = "completed"
        subtitle_jobs[job_id]["result_video"] = final_video
        logger.info(f"[{job_id}] Legendas concluídas. Vídeo salvo em {final_video}")
        
    except Exception as e:
        logger.error(f"[{job_id}] Erro ao gerar legendas: {e}")
        subtitle_jobs[job_id]["status"] = "failed"
        subtitle_jobs[job_id]["error"] = str(e)

@router.post("/generate")
async def generate_subtitles(request: SubtitleRequest, background_tasks: BackgroundTasks):
    """
    Endpoint para gerar legendas locais usando Vosk/Whisper e embutir no vídeo com FFmpeg.
    """
    if not os.path.exists(request.media_path):
        raise HTTPException(status_code=400, detail="Mídia de entrada não encontrada localmente.")

    job_id = f"sub_{uuid.uuid4().hex[:8]}"
    subtitle_jobs[job_id] = {
        "status": "queued",
        "req": request.model_dump(),
        "job_id": job_id
    }
    
    background_tasks.add_task(process_subtitle_job, job_id, request)
    
    return {
        "status": "success",
        "job_id": job_id,
        "message": "Tarefa de geração de legendas iniciada localmente."
    }

@router.get("/status/{job_id}")
async def get_subtitle_status(job_id: str):
    job = subtitle_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return job
