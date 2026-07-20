import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.dark_facil_engine import DarkFacilEngine

router = APIRouter(prefix="/api/v1/dark-facil", tags=["Canal Dark Facil"])

class DarkFacilRequest(BaseModel):
    midias: List[str]
    audio: str
    configs: Optional[Dict[str, Any]] = None

@router.post("/start")
def api_start_dark_facil(req: DarkFacilRequest, background_tasks: BackgroundTasks):
    engine = DarkFacilEngine(configs=req.configs)
    
    def task():
        try:
            engine.run_dark_facil({"midias": req.midias, "audio": req.audio})
        except Exception as e:
            print(f"Erro no Dark Facil: {e}")
            
    background_tasks.add_task(task)
    return {"message": "Processamento Dark Facil iniciado em background"}
