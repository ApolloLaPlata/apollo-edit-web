from fastapi import APIRouter
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("SystemLogger")
router = APIRouter()

# Fila em memoria temporaria para a Rádio (Depois pode ser migrado para o banco)
fila_radio = []

@router.get("/next-action")
async def get_next_action():
    """
    Endpoint chamado pela Antena (Oracle 2) a cada X segundos ou fim de música.
    O Oracle só precisa ler isso para saber qual é o próximo áudio a ser injetado no FFmpeg.
    """
    if fila_radio:
        next_item = fila_radio.pop(0)
        logger.info(f"📻 [Broadcaster] Enviando próxima ação para a Antena: {next_item['action']}")
        return JSONResponse(content=next_item)
    
    # Se a fila estiver vazia, manda a Antena tocar um standby (música de fundo genérica ou loop)
    # Enquanto o Cérebro (Cerbero/Maestro) gera novos conteúdos no Modal/Lightning.
    return JSONResponse(content={
        "action": "standby",
        "audio_url": "standby", # O Oracle pode ter um audio local de fallback
        "metadata": {
            "title": "Aguardando próxima transmissão...",
            "artist": "Apollo Central"
        }
    })

@router.post("/enqueue")
async def enqueue_action(payload: dict):
    """
    Endpoint interno/seguro para os Agentes de Inteligência (Maestro/Zelador)
    adicionarem novas falas ou músicas geradas na fila da Rádio.
    """
    fila_radio.append(payload)
    logger.info(f"📻 [Broadcaster] Nova ação adicionada à fila: {payload.get('action')}")
    return {"status": "success", "fila_tamanho": len(fila_radio)}
