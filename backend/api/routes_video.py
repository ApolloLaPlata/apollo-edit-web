from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

# Importa o orquestrador nativo que criamos
from backend.orchestrator.video_pipeline import PipelineOrchestrator

logger = logging.getLogger("RoutesVideo")
router = APIRouter(prefix="/api/v1/videos", tags=["Videos"])

# Instância Global do Orquestrador
orchestrator = PipelineOrchestrator()

class VideoGenerationRequest(BaseModel):
    tipo_esteira: str  # Ex: 'dark_channel', 'traditional_edit'
    tema: str
    copiloto_id: str   # Ex: 'ChatGPT-4', 'Llama-3'
    instrucoes_adicionais: Optional[str] = None
    user_id: str

@router.post("/generate")
async def generate_video(request: VideoGenerationRequest):
    """
    Endpoint principal acionado pelo Frontend (React) para gerar um novo vídeo.
    Recebe os dados do formulário e joga na esteira correta.
    """
    # 1. Verifica Economia e Debita
    from backend.financial_agent.coin_ledger import charge_operation
    res = charge_operation(request.user_id, "generate_script_short")
    if not res.get("success"):
        raise HTTPException(status_code=402, detail=f"Saldo insuficiente. {res.get('details')}")
    logger.info(f"Recebido pedido de geração de vídeo. Esteira: {request.tipo_esteira}, Tema: {request.tema}")
    
    request_data = {
        "tema": request.tema,
        "copiloto": request.copiloto_id,
        "instrucoes": request.instrucoes_adicionais,
        "user_id": request.user_id
    }
    
    try:
        # Coloca o pedido na fila de renderização assíncrona ao invés de bloquear a rota HTTP
        from backend.services.render_queue import render_queue
        await render_queue.add_task(orchestrator.run_pipeline, request.tipo_esteira, request_data)
        
        return {"status": "success", "message": "Vídeo adicionado à fila de renderização. Acompanhe o progresso na interface."}
    except ValueError as ve:
        logger.error(f"Erro de Validação na Esteira: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Erro Crítico na Geração: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no Servidor Apollo durante a geração do vídeo.")
