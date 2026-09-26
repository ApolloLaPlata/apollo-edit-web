from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from backend.orchestrator.radio_pipeline import radio_manager

logger = logging.getLogger("RoutesRadio")
router = APIRouter(prefix="/api/v1/radio", tags=["Radio 24/7"])

class RadioStartRequest(BaseModel):
    veo_folder: str
    out_folder: str

@router.post("/start")
async def start_radio_stream(request: RadioStartRequest):
    started = await radio_manager.start_radio(request.veo_folder, request.out_folder)
    if started:
        return {"status": "success", "message": "F�brica Infinita da R�dio iniciada em background."}
    else:
        return {"status": "warning", "message": "A R�dio j� est� rodando."}

@router.post("/stop")
async def stop_radio_stream():
    radio_manager.stop_radio()
    return {"status": "success", "message": "F�brica Infinita da R�dio interrompida."}

@router.get("/status")
async def get_radio_status():
    return {"is_running": radio_manager.is_running}

class RadioMixRequest(BaseModel):
    out_folder: str
    music_prompt: str = ""

@router.post("/mix")
async def mix_radio_stream(request: RadioMixRequest):
    success = await radio_manager.mix_radio(request.out_folder, request.music_prompt)
    if success:
        return {"status": "success", "message": "Estação inteira foi mixada em FINAL_RENDER.mp4"}
    else:
        raise HTTPException(status_code=500, detail="Erro na mixagem. Verifique os logs.")
