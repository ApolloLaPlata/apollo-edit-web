import os
import json
import httpx
import uuid
import asyncio
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/studio/modal", tags=["Studio Modal Proxy"])

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cloud_tools", "cloud_accounts_db.json"))

JOBS = {}

def get_active_modal_account():
    if not os.path.exists(DB_FILE):
        return None
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            accounts = json.load(f)
        except:
            return None
    for acc in accounts:
        if acc.get("provider") == "modal" and acc.get("is_active"):
            return acc
    return None

async def process_modal_job(job_id: str, method: str, url: str, headers: dict, body: bytes):
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
            try:
                content = response.json()
            except:
                content = response.text
                
            JOBS[job_id] = {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "content": content
            }
        except Exception as e:
            JOBS[job_id] = {
                "status": "error",
                "status_code": 500,
                "content": {"error": str(e)}
            }

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(status_code=200, content=JOBS[job_id])

@router.api_route("/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_to_modal(path: str, request: Request, background_tasks: BackgroundTasks):
    if request.method == "OPTIONS":
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    acc = get_active_modal_account()
    if not acc:
        raise HTTPException(status_code=503, detail="Nenhuma conta Modal ativa configurada na Colmeia.")
        
    workspace = acc.get("workspace")
    if not workspace:
        raise HTTPException(status_code=500, detail="Workspace modal nao configurado.")

    remote_path = path
    if path == "generate_image":
        remote_path = "generate/image"
    elif path == "generate_video":
        remote_path = "generate/video"
    elif path == "generate_universal":
        remote_path = "generate/universal"
        
    modal_url = f"https://{workspace}--apollo-render-router-apollo-api.modal.run/{remote_path}"
    
    headers = {}
    if acc.get("proxy_secret"):
        headers["Authorization"] = f"Bearer {acc.get('proxy_secret')}"
    
    if "content-type" in request.headers:
        headers["Content-Type"] = request.headers["content-type"]
            
    body = await request.body()
    
    # Se for uma das rotas demoradas, usar Background Task
    if path in ["generate_image", "generate_video", "generate_universal"] and request.method == "POST":
        job_id = str(uuid.uuid4())
        JOBS[job_id] = {"status": "processing"}
        background_tasks.add_task(process_modal_job, job_id, request.method, modal_url, headers, body)
        return JSONResponse(status_code=200, content={"status": "processing", "job_id": job_id})
    
    # Execucao sincrona para outras rotas (como ping, models)
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=modal_url,
                headers=headers,
                content=body
            )
            try:
                content = response.json()
            except:
                content = response.text
                
            return JSONResponse(
                status_code=response.status_code,
                content=content
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

