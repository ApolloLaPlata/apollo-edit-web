import os
import json
import time
import uuid
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

load_dotenv()

app = FastAPI(title="Apollo Maestro - Lightning API Gateway")

def get_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

CONFIG = get_config()

# Serve media outputs (where load balancer saves downloaded files)
media_dir = os.path.join(os.path.dirname(__file__), "temp_outputs")
os.makedirs(media_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_dir), name="media")

# Permite que o frontend (HTML/JS) faça requisições para este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LIGHTNING_API_KEY = os.getenv("LIGHTNING_API_KEY", "")

# Configuração da Lightning Inference API (Plano A)
LIGHTNING_BASE_URL = "https://api.lightning.ai/v1"

# Banco de dados em memória para os Jobs
jobs_db = {}

class ChatRequest(BaseModel):
    user_id: str
    prompt: str
    system_prompt: str = "Você é o Apollo, um assistente inteligente."
    model: str = "openai/gpt-5"

class GenerationRequest(BaseModel):
    user_id: str
    model: str
    prompt: str
    cost_in_crystals: int = 1

def deduct_crystals(user_id: str, cost: int) -> bool:
    print(f"[Banco de Dados] Cobrando {cost} cristal(is) do usuário {user_id}...")
    return True

def refund_crystals(user_id: str, cost: int):
    print(f"[Banco de Dados] REEMBOLSANDO {cost} cristal(is) para o usuário {user_id}.")

async def call_load_balancer_api(job_id: str, req: GenerationRequest):
    """
    Envia a requisição de geração para o nosso próprio Load Balancer.
    Ele é o responsável por acordar a máquina, rotear e aplicar o retry-loop.
    """
    model_name = req.model
    jobs_db[job_id]["status"] = "processing_on_api"
    print(f"[{job_id}] Enviando requisição para o Load Balancer (modelo: {model_name})...")
    
    try:
        # Load Balancer local (porta 8000)
        lb_endpoint = "http://127.0.0.1:8000/route"
        payload = {
            "model": model_name,
            "prompt": req.prompt,
            "job_id": job_id
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(lb_endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            
        jobs_db[job_id]["status"] = "completed"
        # O resultado do LitServe geralmente vem dentro de "data" retornado pelo router
        litserve_response = data.get("data", {})
        # Tentamos extrair url ou salvamos o objeto bruto
        file_url = litserve_response.get("url") or litserve_response.get("file_url") or "https://picsum.photos/1024"
        jobs_db[job_id]["result"] = {"file_url": file_url, "raw_data": litserve_response}
        print(f"[{job_id}] Geração concluída via Load Balancer.")
        
    except Exception as e:
        print(f"[{job_id}] ERRO NO LOAD BALANCER: {e}")
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error"] = str(e)
        refund_crystals(req.user_id, req.cost_in_crystals)

@app.post("/generate")
async def generate_media(req: GenerationRequest, background_tasks: BackgroundTasks):
    if not deduct_crystals(req.user_id, req.cost_in_crystals):
        raise HTTPException(status_code=402, detail="Cristais insuficientes.")

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    jobs_db[job_id] = {
        "status": "queued",
        "user_id": req.user_id,
        "model": req.model,
        "prompt": req.prompt
    }

    background_tasks.add_task(call_load_balancer_api, job_id, req)

    return {
        "status": "success",
        "job_id": job_id,
        "message": "Enviado para a Lightning AI!"
    }

@app.post("/chat")
async def generate_chat(req: ChatRequest):
    """Endpoint direto para o Chatbot (Serverless API Lightning). Não liga máquina."""
    if not deduct_crystals(req.user_id, 1):
        raise HTTPException(status_code=402, detail="Cristais insuficientes.")

    chat_cfg = CONFIG.get("api_config", {}).get("lightning_chat", {})
    api_key = chat_cfg.get("api_key", "")
    base_url = chat_cfg.get("base_url", "https://lightning.ai/api/v1/chat/completions")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="Chave do lightning_chat não configurada.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": req.system_prompt},
            {"role": "user", "content": [{"type": "text", "text": req.prompt}]}
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"status": "success", "reply": reply}
    except Exception as e:
        refund_crystals(req.user_id, 1)
        print(f"[Chatbot ERRO] {e}")
        raise HTTPException(status_code=500, detail=f"Erro na API Serverless da Lightning: {str(e)}")

@app.get("/status/{job_id}")
async def check_job_status(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    return job

if __name__ == "__main__":
    import uvicorn
    print("="*50)
    print("MAESTRO INICIADO - CONECTADO A LIGHTNING AI")
    if not LIGHTNING_API_KEY:
        print("AVISO: MODO SIMULACAO ATIVADO (Chave API nao encontrada)")
        print("Para producao, defina a variavel: set LIGHTNING_API_KEY=sua_chave")
    print("="*50)
    uvicorn.run(app, host="0.0.0.0", port=3000)
