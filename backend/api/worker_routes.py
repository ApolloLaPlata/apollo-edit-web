from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
import uuid
import asyncio

# Usamos o load balancer local e o phantom manager
from backend.cloud_tools.load_balancer import active_jobs, completed_jobs
from backend.api.routes_phantom import phantom_manager

router = APIRouter(prefix="/jobs", tags=["Workers"])

class JobRequest(BaseModel):
    action: str  # ex: "edge_tts", "generate_broll", "remove_bg"
    prompt: str
    target_extension_id: str = "meta_ext_1"  # ID do phantom node
    role: str = "general"

@router.post("/dispatch")
async def dispatch_worker_job(job: JobRequest):
    """
    Despacha uma tarefa diretamente para uma extensão Phantom Fleet via WebSocket.
    Se no futuro houver nós Lightning padrão, podemos rotear via Load Balancer.
    Por enquanto, usa a rotação WebSocket do Phantom Manager.
    """
    task_id = str(uuid.uuid4())
    
    # Executa a chamada via WebSocket e aguarda a resposta (timeout de 5 min)
    response = await phantom_manager.dispatch_task(
        extension_id=job.target_extension_id,
        task_id=task_id,
        action=job.action,
        prompt=job.prompt,
        timeout=300
    )
    
    if response and response.get("status") == "error":
        raise HTTPException(status_code=504, detail=response.get("message"))
        
    return {
        "status": "success", 
        "task_id": task_id,
        "message": f"Job {job.action} processado pela nuvem.",
        "result": response
    }
