from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
import modal
import os
import uuid
import asyncio

router = APIRouter(prefix="/api/audio", tags=["Audio"])

class AudioGenRequest(BaseModel):
    prompt: str
    lyrics: str = ""
    duration: int = 15
    engine: str = "acestep" # "acestep" ou "yue" ou "sa3" ou "minimax"

# Armazenamento simples em memria para os jobs
# Num sistema real, usar Redis ou DB.
jobs_db = {}

def process_audio_job(job_id: str, req: AudioGenRequest):
    try:
        jobs_db[job_id] = {"status": "processing"}
        print(f"[JOB {job_id}] Iniciando geracao Modal: {req.engine}")
        
        if req.engine == "acestep":
            func = modal.Function.lookup("apollo-render-router", "AceStep15Engine.generate_song")
            tags = req.prompt
            lyrics = req.lyrics if req.lyrics else "[Verse]\n" + req.prompt
            wav_data = func.remote(prompt_tags=tags, lyrics=lyrics)
            filename = f"acestep_{job_id}.wav"
            
        elif req.engine == "sa3":
            func = modal.Function.lookup("apollo-render-router", "StableAudioEngine.generate_audio")
            wav_data = func.remote(prompt=req.prompt, duration_s=float(req.duration))
            filename = f"sa3_{job_id}.wav"
            
        elif req.engine == "minimax":
            func = modal.Function.lookup("apollo-render-router", "MinimaxEngine.generate")
            wav_data = func.remote(prompt=req.prompt, lyrics=req.lyrics, duration=float(req.duration))
            filename = f"minimax_{job_id}.wav"
            
        elif req.engine == "yue":
            jobs_db[job_id] = {"status": "error", "error": "YuE engine not deployed yet."}
            return
            
        else:
            jobs_db[job_id] = {"status": "error", "error": "Motor desconhecido"}
            return
            
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
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return job
