import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.clip_factory import MusicVideoEngine

router = APIRouter(prefix="/api/v1/clip-factory", tags=["Fabrica de Clipes"])

class GenerateClipRequest(BaseModel):
    musica_path: str
    bg_folder: str
    saida_path: str
    configs: Optional[Dict[str, Any]] = None

@router.post("/generate")
def api_generate_clip(req: GenerateClipRequest, background_tasks: BackgroundTasks):
    engine = MusicVideoEngine(configs=req.configs)
    
    def task():
        try:
            engine.generate_music_video(req.musica_path, req.bg_folder, req.saida_path)
        except Exception as e:
            print(f"Erro na Fabrica de Clipes: {e}")
            
    background_tasks.add_task(task)
    return {"message": "Geracao de clipe iniciada em background"}
