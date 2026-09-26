from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import asyncio
import uuid
import json
import logging

logger = logging.getLogger("TimelineExport")

class TimelineExportRequest(BaseModel):
    project_name: str
    export_time: str
    clips: List[Dict[str, Any]]
    draft_mode: bool = False
    export_resolution: str = "1080p"
    export_fps: str = "30"
    export_quality: str = "alta"

router = APIRouter(prefix="/api/v1/editor", tags=["Timeline Export"])

async def process_timeline_export(job_id: str, payload: TimelineExportRequest):
    try:
        logger.info(f"Iniciando exportacao da timeline {job_id}")
        # Simulando mapeamento dos arquivos para FFmpeg
        # (Em producao real, montamos filter_complex com trim_in e start_time)
        clips = sorted(payload.clips, key=lambda c: c.get('start_time', 0))
        if not clips:
            logger.error("Nenhum clip encontrado")
            return
            
        output_file = f"public/exports/{payload.project_name}_{job_id}.mp4"
        os.makedirs("public/exports", exist_ok=True)
        
        # Filtro complex simples: apenas concatena de forma basica para MVP
        inputs = []
        filter_str = ""
        for i, clip in enumerate(clips):
            if clip['type'] in ['video', 'audio']:
                # Pega o caminho real do dataset, como é um mock visual, vamos tentar achar
                name = clip.get('name', '')
                path = f"public/media/{name}" # Aproximacao do caminho real
                
                if os.path.exists(path):
                    inputs.extend(["-i", path])
                    trim_in = clip.get('trim_in', 0)
                    duration = clip.get('duration', 5)
                    # Simples trim
                    filter_str += f"[{i}:v]trim=start={trim_in}:duration={duration},setpts=PTS-STARTPTS,scale=1920:1080[v{i}];"
                    filter_str += f"[{i}:a]atrim=start={trim_in}:duration={duration},asetpts=PTS-STARTPTS[a{i}];"
                
        if not inputs:
            logger.error("Nenhum arquivo de video valido encontrado no disco.")
            return
            
        concat_v = "".join([f"[v{i}]" for i in range(len(inputs)//2)])
        concat_a = "".join([f"[a{i}]" for i in range(len(inputs)//2)])
        filter_str += f"{concat_v}concat=n={len(inputs)//2}:v=1:a=0[outv];"
        filter_str += f"{concat_a}concat=n={len(inputs)//2}:v=0:a=1[outa]"
        
        cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, "-map", "[outv]", "-map", "[outa]", output_file]
        
        logger.info(f"Executando FFmpeg: {' '.join(cmd)}")
        # Executar FFmpeg async
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info(f"Exportacao concluida com sucesso: {output_file}")
        else:
            logger.error(f"Erro FFmpeg: {stderr.decode()}")
            
    except Exception as e:
        logger.error(f"Falha na exportacao: {str(e)}")


@router.post("/export_timeline")
def export_timeline(req: TimelineExportRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(process_timeline_export, job_id, req)
    return {"status": "success", "message": "Renderizacao iniciada no backend FFmpeg", "job_id": job_id}
