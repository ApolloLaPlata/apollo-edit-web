"""
routes_ui_ws.py — WebSocket para a Interface do Usuário (Frontend Web)
======================================================================
Permite que os Agentes Autônomos (Mascote, Copiloto, Maestro, Concierge)
enviem notificações, mensagens de chat e atualizações de progresso
diretamente para a tela do usuário em tempo real.

Endpoint:
  WS /ws/ui/{user_id}
"""

import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

logger = logging.getLogger("UI_WebSocket")

router = APIRouter(tags=["UI_WebSocket"])

class UIConnectionManager:
    def __init__(self):
        # user_id -> WebSocket
        self.active_users: Dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket, user_id: str):
        await ws.accept()
        self.active_users[user_id] = ws
        logger.info(f"[UI_WS] 👤 Usuário {user_id} abriu a interface do Apollo.")

    def disconnect(self, user_id: str):
        if user_id in self.active_users:
            del self.active_users[user_id]
            logger.info(f"[UI_WS] 🚪 Usuário {user_id} fechou a interface do Apollo.")

    async def send_to_user(self, user_id: str, message_type: str, payload: dict):
        """Envia um evento em tempo real para um usuário específico na UI."""
        if user_id in self.active_users:
            ws = self.active_users[user_id]
            message = {
                "type": message_type,
                "payload": payload
            }
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"[UI_WS] Erro ao enviar para {user_id}: {e}")
                self.disconnect(user_id)
        else:
            logger.debug(f"[UI_WS] Usuário {user_id} offline. Mensagem descartada.")

    async def broadcast(self, message_type: str, payload: dict):
        """Envia um evento em tempo real para TODOS os usuários na UI."""
        message = {
            "type": message_type,
            "payload": payload
        }
        for user_id, ws in list(self.active_users.items()):
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"[UI_WS] Erro no broadcast para {user_id}: {e}")
                self.disconnect(user_id)

# Instância global do gerenciador da UI
ui_ws_manager = UIConnectionManager()


@router.websocket("/ws/ui/{user_id}")
async def websocket_ui_endpoint(websocket: WebSocket, user_id: str):
    await ui_ws_manager.connect(websocket, user_id)
    try:
        while True:
            # Mantém a conexão aberta escutando pings ou mensagens do client (se houver)
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                # Podemos processar interações do usuário com o mascote aqui
                logger.debug(f"[UI_WS] Mensagem do {user_id}: {data}")
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ui_ws_manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"[UI_WS] Erro na conexão com {user_id}: {e}")
        ui_ws_manager.disconnect(user_id)
