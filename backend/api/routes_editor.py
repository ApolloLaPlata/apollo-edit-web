import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.basic_editor import gerar_video
from backend.services.audio_video_tools import extrair_audio, remover_audio, inverter_video, comprimir_video

router = APIRouter(prefix="/api/v1/editor", tags=["Editor Basico e Ferramentas"])

class GenerateVideoRequest(BaseModel):
    payload: Dict[str, Any]

class ToolRequest(BaseModel):
    video_path: str
    output_path: str
    params: Optional[Dict[str, Any]] = None

@router.post("/generate")
def api_generate_video(req: GenerateVideoRequest, background_tasks: BackgroundTasks):
    # Roda a edicao avancada (antiga AbaEdicaoBasica) em background
    def task():
        try:
            gerar_video(req.payload)
        except Exception as e:
            print(f"Erro na edicao basica: {e}")
    background_tasks.add_task(task)
    return {"message": "Geracao de video iniciada em background"}

@router.post("/tools/extract_audio")
def api_extract_audio(req: ToolRequest):
    try:
        res = extrair_audio(req.video_path, req.output_path)
        return {"success": True, "output": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/remove_audio")
def api_remove_audio(req: ToolRequest):
    try:
        res = remover_audio(req.video_path, req.output_path)
        return {"success": True, "output": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/invert_video")
def api_invert_video(req: ToolRequest):
    try:
        res = inverter_video(req.video_path, req.output_path)
        return {"success": True, "output": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/compress_video")
def api_compress_video(req: ToolRequest):
    try:
        crf = req.params.get('crf', '28') if req.params else '28'
        res = comprimir_video(req.video_path, req.output_path, crf)
        return {"success": True, "output": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
