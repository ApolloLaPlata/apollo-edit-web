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
            func = modal.Function.lookup("ace-step-music-engine", "AceStepEngine.generate_song")
            
            # Executar de forma assíncrona na nuvem
            tags = req.prompt
            lyrics = req.lyrics if req.lyrics else "[Verse]\n" + req.prompt
            
            # Modal functions can be awaited using .aio()
            wav_data = await func.remote.aio(prompt_tags=tags, lyrics=lyrics)
            
            filename = f"acestep_{uuid.uuid4().hex[:8]}.wav"
            # Salvar no diretório público para o frontend tocar
            out_dir = os.path.join(os.getcwd(), "Midias", "Audios")
            os.makedirs(out_dir, exist_ok=True)
            
            out_path = os.path.join(out_dir, filename)
            with open(out_path, "wb") as f:
                f.write(wav_data)
                
            return {"status": "success", "file_url": f"/Midias/Audios/{filename}", "engine": "acestep"}
            
        elif req.engine == "yue":
            # TODO: Add YuE support once deployed
            return {"status": "pending", "message": "YuE engine not deployed yet."}
            
        else:
            raise HTTPException(status_code=400, detail="Motor desconhecido")
            
    except Exception as e:
        print(f"Erro na geração de áudio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
