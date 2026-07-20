import os
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.services.render_queue import RenderQueueManager

router = APIRouter(prefix="/api/v1/queue", tags=["Fila de Render"])

queue_manager = RenderQueueManager()

class JobRequest(BaseModel):
    job_data: Dict[str, Any]

@router.get("/")
def api_get_queue():
    return {"queue": queue_manager.get_queue()}

@router.post("/add")
def api_add_job(req: JobRequest):
    return queue_manager.add_job(req.job_data)

@router.post("/run")
def api_run_queue(background_tasks: BackgroundTasks):
    def task():
        try:
            queue_manager.run_queue()
        except Exception as e:
            print(f"Erro na Fila de Render: {e}")
            
    background_tasks.add_task(task)
    return {"message": "Fila de renderização iniciada em background"}
