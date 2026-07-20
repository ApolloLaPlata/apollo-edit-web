"""
routes_whatsapp.py — Rotas do WhatsApp Webhook
===============================================
Recebe as mensagens do WhatsApp Bridge (Node.js → Python) e
as encaminha para o Maestro processar e responder.

Endpoint principal:
  POST /api/whatsapp/webhook  ← recebe mensagens do Bridge Node.js
  GET  /api/whatsapp/status   ← verifica se a bridge está online
  POST /api/whatsapp/send     ← permite envio manual via admin
"""

import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from backend.agents.whatsapp_bridge import whatsapp_bridge

logger = logging.getLogger("WhatsAppRoutes")

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

# Referência ao Maestro (será injetada no startup do main.py)
_maestro_ref = None

def set_maestro(maestro_instance):
    """Injeta a referência do Maestro nas rotas. Chamado no startup."""
    global _maestro_ref
    _maestro_ref = maestro_instance
    logger.info("[WA Routes] Maestro injetado com sucesso nas rotas WhatsApp.")


# ─────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────
class IncomingMessage(BaseModel):
    """Payload enviado pelo Bridge Node.js para cá."""
    from_: str = Field(alias="from") # Número de origem (campo 'from' é keyword em Python)
    to: str
    body: str
    timestamp: Optional[int] = None
    sender_name: Optional[str] = "Usuário"


class ManualSendRequest(BaseModel):
    to: str
    message: str
    level: Optional[str] = "info"  # info | warning | critical | emergency


# ─────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────
@router.post("/webhook")
async def receive_whatsapp_message(request: Request):
    """
    Recebe mensagem do Bridge Node.js.
    A bridge envia: { from, to, body, timestamp, sender_name }
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido.")

    from_number = data.get("from", "")
    body        = data.get("body", "").strip()
    sender_name = data.get("sender_name", "Usuário")

    if not body:
        return {"status": "ignored", "reason": "Mensagem vazia."}

    logger.info(f"[WA Webhook] 📩 Recebido de {from_number} ({sender_name}): '{body[:60]}...'")

    # Encaminha para o Maestro processar
    if _maestro_ref is None:
        logger.warning("[WA Webhook] Maestro não injetado ainda. Mensagem descartada.")
        return {"status": "error", "reason": "Maestro não disponível."}

    try:
        response_text = await _maestro_ref.process_ceo_command(body)

        if response_text:
            # Responde de volta para quem enviou
            await whatsapp_bridge.send(from_number, response_text)
            logger.info(f"[WA Webhook] ✅ Resposta enviada para {from_number}")

        return {"status": "processed", "reply_sent": bool(response_text)}

    except Exception as e:
        logger.error(f"[WA Webhook] ❌ Erro ao processar mensagem: {e}")
        return {"status": "error", "error": str(e)}


@router.get("/status")
async def whatsapp_status():
    """Verifica se a Bridge Node.js está online e conectada ao WhatsApp."""
    status = await whatsapp_bridge.get_status()
    return {
        "bridge_online": status["online"],
        "whatsapp_status": status["whatsapp_status"],
        "message": "Bridge conectada ao WhatsApp ✅" if status["whatsapp_status"] == "CONNECTED"
                   else "Bridge offline ou aguardando QR Code ⚠️"
    }


@router.post("/send")
async def manual_send(req: ManualSendRequest):
    """Envia uma mensagem manualmente via painel admin."""
    if req.level != "info":
        success = await whatsapp_bridge.send_alert(req.level, req.message)
    else:
        success = await whatsapp_bridge.send(req.to, req.message)

    if success:
        return {"status": "sent", "to": req.to}
    raise HTTPException(status_code=503, detail="Falha ao enviar mensagem. Bridge offline?")
