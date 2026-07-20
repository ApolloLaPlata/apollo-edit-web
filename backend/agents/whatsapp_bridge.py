"""
whatsapp_bridge.py — Ponte Python ↔ WhatsApp Bridge Node.js
============================================================
Módulo centralizado para ENVIAR e RECEBER mensagens do WhatsApp via
a bridge Node.js que já está rodando na porta 5001.

Uso interno:
  from backend.agents.whatsapp_bridge import whatsapp_bridge
  await whatsapp_bridge.send("+5511999999999@c.us", "Texto da mensagem")
  await whatsapp_bridge.send_alert("🚨 Alerta crítico: disco cheio!")
"""

import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("WhatsAppBridge")

# ─────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────
WHATSAPP_BRIDGE_URL = os.getenv("WHATSAPP_BRIDGE_URL", "http://127.0.0.1:5001")
CEO_WHATSAPP_NUMBER = os.getenv("CEO_WHATSAPP_NUMBER", "")  # Ex: "5511999999999@c.us"

# Número formatado como ID do WhatsApp (padrão: DDI+DDD+número@c.us)
def _format_number(raw: str) -> str:
    """Garante que o número está no formato correto para a API."""
    if not raw:
        return ""
    raw = raw.strip().replace("+", "").replace(" ", "").replace("-", "")
    if "@c.us" not in raw:
        raw = f"{raw}@c.us"
    return raw


class WhatsAppBridge:
    """
    Interface Python para a bridge Node.js do WhatsApp.
    Suporta envio de mensagens simples, alertas formatados e comandos CEO.
    """

    async def send(self, to: str, message: str) -> bool:
        """
        Envia uma mensagem de texto para um número/grupo no WhatsApp.
        `to` deve estar no formato: '5511999999999@c.us' (DM) ou 'ID@g.us' (Grupo).
        """
        to = _format_number(to) if "@g.us" not in to else to

        if not to:
            logger.warning("[WA Bridge] ⚠️ Número de destino não configurado. Ignorando envio.")
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{WHATSAPP_BRIDGE_URL}/api/send",
                    json={"to": to, "message": message}
                )
                if resp.status_code == 200:
                    logger.info(f"[WA Bridge] ✅ Mensagem enviada para {to[:20]}...")
                    return True
                else:
                    logger.error(f"[WA Bridge] ❌ Falha ao enviar: HTTP {resp.status_code} — {resp.text}")
                    return False
        except httpx.ConnectError:
            logger.warning("[WA Bridge] ⚠️ Bridge Node.js offline (porta 5001). Mensagem descartada.")
            return False
        except Exception as e:
            logger.error(f"[WA Bridge] ❌ Erro inesperado: {e}")
            return False

    async def send_to_ceo(self, message: str) -> bool:
        """Envia uma mensagem diretamente para o número do CEO."""
        if not CEO_WHATSAPP_NUMBER:
            logger.warning("[WA Bridge] ⚠️ CEO_WHATSAPP_NUMBER não configurado no .env")
            return False
        return await self.send(CEO_WHATSAPP_NUMBER, message)

    async def send_alert(self, level: str, message: str) -> bool:
        """
        Envia um alerta formatado ao CEO com emoji por nível de severidade.
        Níveis: 'info', 'warning', 'critical', 'emergency'
        """
        emojis = {
            "info":      "ℹ️",
            "warning":   "⚠️",
            "critical":  "🚨",
            "emergency": "🆘",
        }
        emoji = emojis.get(level, "📢")
        formatted = f"{emoji} *Apollo Alert [{level.upper()}]*\n\n{message}"
        return await self.send_to_ceo(formatted)

    async def get_status(self) -> dict:
        """Verifica se a bridge Node.js está online e conectada ao WhatsApp."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{WHATSAPP_BRIDGE_URL}/api/status")
                data = resp.json()
                return {"online": True, "whatsapp_status": data.get("status", "UNKNOWN")}
        except Exception:
            return {"online": False, "whatsapp_status": "OFFLINE"}


# Singleton global
whatsapp_bridge = WhatsAppBridge()
