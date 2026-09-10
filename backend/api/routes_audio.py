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
    engine: str = "acestep" # "acestep" ou "yue"

@router.post("/generate")
async def generate_audio(req: AudioGenRequest):
    try:
        if req.engine == "acestep":
            # Usar o Modal Function Lookup para buscar o App deployado
            func = modal.Function.lookup("apollo-render-router", "AceStep15Engine.generate_song")
            
            # Executar de forma assíncrona na nuvem
            tags = req.prompt
            lyrics = req.lyrics if req.lyrics else "[Verse]\n" + req.prompt
            
            # Modal functions can be awaited using .aio()
            wav_data = await func.remote.aio(prompt_tags=tags, lyrics=lyrics)
            
            filename = f"acestep_{uuid.uuid4().hex[:8]}.wav"
            
        elif req.engine == "sa3":
            func = modal.Function.lookup("apollo-render-router", "StableAudioEngine.generate_audio")
            wav_data = await func.remote.aio(prompt=req.prompt, duration_s=float(req.duration))
            filename = f"sa3_{uuid.uuid4().hex[:8]}.wav"
            
        elif req.engine == "minimax":
            func = modal.Function.lookup("apollo-render-router", "MinimaxEngine.generate")
            wav_data = await func.remote.aio(prompt=req.prompt, lyrics=req.lyrics, duration=float(req.duration))
            filename = f"minimax_{uuid.uuid4().hex[:8]}.wav"
            
        elif req.engine == "yue":
            # TODO: Add YuE support once deployed
            return {"status": "pending", "message": "YuE engine not deployed yet."}
            
        else:
            raise HTTPException(status_code=400, detail="Motor desconhecido")
            
        # Salvar no diretório público para o frontend tocar
        out_dir = os.path.join(os.getcwd(), "Midias", "Audios")
        os.makedirs(out_dir, exist_ok=True)
        
        out_path = os.path.join(out_dir, filename)
        with open(out_path, "wb") as f:
            f.write(wav_data)
            
        return {"status": "success", "file_url": f"/Midias/Audios/{filename}", "engine": req.engine}
            
    except Exception as e:
        print(f"Erro na geração de áudio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
