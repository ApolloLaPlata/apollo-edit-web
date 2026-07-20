import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.auto_mapper import AutoMapperEngine

router = APIRouter(prefix="/api/v1/auto-mapper", tags=["Mapeador Automatico"])

class MappingRequest(BaseModel):
    modo: str
    videos: List[str]
    configs: Optional[Dict[str, Any]] = None

@router.post("/start")
def api_start_mapping(req: MappingRequest, background_tasks: BackgroundTasks):
    engine = AutoMapperEngine(configs=req.configs)
    
    def task():
        try:
            engine.run_mapping({"modo": req.modo, "videos": req.videos})
        except Exception as e:
            print(f"Erro no Mapeador Automatico: {e}")
            
    background_tasks.add_task(task)
    return {"message": "Mapeamento automatico iniciado em background"}
