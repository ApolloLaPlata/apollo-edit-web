"""
routes_phantom.py — WebSocket para a Phantom Fleet (Extensões Chrome)
=====================================================================
Permite que as extensões de navegador injetadas (ex: no Meta, NanoBanana, etc.)
se conectem via WebSocket e recebam comandos em tempo real do Backend do Apollo.

Endpoint:
  WS /ws/phantom/{extension_id}
"""

import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

logger = logging.getLogger("PhantomFleet")

router = APIRouter(tags=["PhantomFleet"])

class PhantomConnectionManager:
    def __init__(self):
        # extension_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # task_id -> async event (para aguardar o retorno da extensão)
        self.pending_tasks: Dict[str, dict] = {}

    async def connect(self, ws: WebSocket, extension_id: str):
        await ws.accept()
        self.active_connections[extension_id] = ws
        logger.info(f"[Phantom] 👻 Conexão estabelecida: {extension_id}")

    def disconnect(self, extension_id: str):
        if extension_id in self.active_connections:
            del self.active_connections[extension_id]
            logger.info(f"[Phantom] 🔌 Conexão perdida: {extension_id}")

    async def dispatch_task(self, extension_id: str, task_id: str, action: str, prompt: str, timeout: int = 300) -> dict:
        """
        Envia uma tarefa para a extensão via WS e aguarda a resposta.
        """
        if extension_id not in self.active_connections:
            return {"status": "error", "message": f"Extensão {extension_id} não conectada."}
        
        ws = self.active_connections[extension_id]
        
        # Cria um evento assíncrono para esperar a resposta
        event = asyncio.Event()
        self.pending_tasks[task_id] = {"event": event, "response": None}
        
        payload = {
            "action": action,
            "task_id": task_id,
            "prompt": prompt
        }
        
        try:
            await ws.send_text(json.dumps(payload))
            logger.info(f"[Phantom] 📤 Tarefa {task_id} ('{action}') enviada para {extension_id}")
            
            # Aguarda a extensão responder ou timeout
            await asyncio.wait_for(event.wait(), timeout=timeout)
            
            response = self.pending_tasks[task_id]["response"]
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"[Phantom] ⏱️ Timeout aguardando {extension_id} para a tarefa {task_id}")
            return {"status": "error", "message": "Timeout aguardando a extensão."}
        except Exception as e:
            logger.error(f"[Phantom] ❌ Erro ao enviar para {extension_id}: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            if task_id in self.pending_tasks:
                del self.pending_tasks[task_id]

    def handle_response(self, data: dict):
        """Processa a resposta que voltou da extensão."""
        task_id = data.get("task_id")
        if task_id and task_id in self.pending_tasks:
            self.pending_tasks[task_id]["response"] = data
            self.pending_tasks[task_id]["event"].set()
            logger.info(f"[Phantom] 📥 Resposta recebida para a tarefa {task_id}")
        else:
            logger.warning(f"[Phantom] ⚠️ Resposta órfã ou desconhecida recebida: {data}")

# Instância global do gerenciador
phantom_manager = PhantomConnectionManager()


@router.websocket("/ws/phantom/{extension_id}")
async def websocket_phantom_endpoint(websocket: WebSocket, extension_id: str):
    await phantom_manager.connect(websocket, extension_id)
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                phantom_manager.handle_response(data)
            except json.JSONDecodeError:
                logger.error(f"[Phantom] Erro ao decodificar JSON de {extension_id}: {data_str}")
    except WebSocketDisconnect:
        phantom_manager.disconnect(extension_id)
    except Exception as e:
        logger.error(f"[Phantom] Erro na conexão com {extension_id}: {e}")
        phantom_manager.disconnect(extension_id)
