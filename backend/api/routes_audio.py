from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
import requests
import json
import os
import uuid
import base64

router = APIRouter(prefix="/api/audio", tags=["Audio"])

class AudioGenRequest(BaseModel):
    prompt: str
    lyrics: str = ""
    duration: int = 15
    engine: str = "acestep" # "acestep" ou "yue" ou "sa3" ou "minimax"

jobs_db = {}

WEBHOOK_URL = 'https://radiodarktrap--apollo-render-router-apollo-api.modal.run/generate/audio_lab'

def process_audio_job(job_id: str, req: AudioGenRequest):
    try:
        jobs_db[job_id] = {"status": "processing"}
        print(f"[JOB {job_id}] Iniciando geracao Webhook: {req.engine}")
        
        # Mapear o nome do engine pro formato que o webhook espera
        engine_map = {
            "acestep": "ace-step",
            "sa3": "sa3",
            "minimax": "minimax"
        }
        
        if req.engine not in engine_map:
            jobs_db[job_id] = {"status": "error", "error": f"Motor nÃ£o suportado pelo webhook: {req.engine}"}
            return
            
        webhook_model = engine_map[req.engine]
        
        payload = {
            'prompt': req.prompt,
            'model': webhook_model,
            'duration': req.duration
        }
        
        # O Webhook costumava suportar letras? Vou mandar na prompt ou como lyrics se aplicavel.
        if req.lyrics:
            payload['lyrics'] = req.lyrics
            
        print(f"[JOB {job_id}] Enviando requisiÃ§Ã£o para {WEBHOOK_URL} com payload: {payload}")
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=600)
        resp.raise_for_status()
        
        lines = [line for line in resp.text.split('\n') if line.strip()]
        if not lines:
            raise ValueError("Resposta vazia do webhook")
            
        last_json = json.loads(lines[-1])
        
        if 'error' in last_json or last_json.get('status') == 'error':
            error_msg = last_json.get('error') or last_json.get('message') or str(last_json)
            raise ValueError(f"Erro no webhook: {error_msg}")
            
        audio_b64 = last_json.get('audio_base64')
        if not audio_b64:
            raise ValueError("Base64 de audio nao encontrado na resposta")
            
        wav_data = base64.b64decode(audio_b64)
        filename = f"{req.engine}_{job_id}.wav"
            
        # Salvar no diretrio pblico
        out_dir = os.path.join(os.getcwd(), "Midias", "Audios")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, filename)
        
        with open(out_path, "wb") as f:
            f.write(wav_data)
            
        jobs_db[job_id] = {
            "status": "success", 
            "file_url": f"/Midias/Audios/{filename}",
            "engine": req.engine
        }
        print(f"[JOB {job_id}] Sucesso. Salvo em {filename}")
        
    except Exception as e:
        print(f"[JOB {job_id}] Erro: {e}")
        jobs_db[job_id] = {"status": "error", "error": str(e)}

@router.post("/generate")
async def generate_audio(req: AudioGenRequest, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex[:8]
    background_tasks.add_task(process_audio_job, job_id, req)
    return {"status": "queued", "job_id": job_id, "message": "Job initiated. Poll /status/{job_id} for results."}

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nÃ£o encontrado")
    return job
