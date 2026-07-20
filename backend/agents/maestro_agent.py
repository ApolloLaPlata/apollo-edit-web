import logging
import json
import os
import asyncio
import time
from typing import Dict, Any

from backend.agents.base_agent import BaseAgent
from backend.agents.whatsapp_bridge import whatsapp_bridge
from backend.router.waterfall_router import WaterfallRouter

logger = logging.getLogger("MaestroAgent")

class MaestroAgent(BaseAgent):
    """
    Agente Gerente Central (O Maestro) - VERSÃO PROATIVA + WHATSAPP REAL.
    Aba do Painel: Visão Geral (Dashboard)

    - Roda um Loop de Consciência avaliando o estado do sistema a cada 1 hora
    - Reage em tempo real a eventos críticos do HiveBus
    - Se comunica com o CEO via WhatsApp Bridge
    - Processa comandos do CEO recebidos via WhatsApp
    """
    def __init__(self, router_instance: WaterfallRouter):
        super().__init__(agent_name="Maestro")
        self.router = router_instance
        self.memory_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'memories')

        # O Maestro escuta TUDO que passa pelo rádio da colmeia
        self.listen("*", self._on_bus_message)

    async def _on_bus_message(self, sender: str, topic: str, payload: Any):
        """O Maestro processa as mensagens de rádio interceptadas."""
        if sender == self.agent_name:
            return  # Ignora os próprios ecos

        logger.info(f"🧠 [Maestro ouviu] {sender} falando sobre '{topic}': {payload}")

        # Grava no log de rádio
        if "radio_logs" not in self.memory_data["data"]:
            self.memory_data["data"]["radio_logs"] = []
        self.memory_data["data"]["radio_logs"].append({
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sender": sender,
            "topic": topic,
            "payload": payload
        })
        # Mantém apenas os últimos 100 logs
        self.memory_data["data"]["radio_logs"] = self.memory_data["data"]["radio_logs"][-100:]
        self.save_memory()

        # --- Reage automaticamente a eventos críticos ---
        if topic == "financial.alert":
            alert_type = payload.get("type", "unknown")

            if alert_type == "account_unhealthy":
                msg = (
                    f"⚠️ *Conta Lightning Offline!*\n"
                    f"A conta *{payload.get('account', 'Desconhecida')}* foi marcada como UNHEALTHY "
                    f"após 3 erros consecutivos.\n"
                    f"Acesse o painel /status para detalhes."
                )
                await self._send_whatsapp_alert("critical", msg)

            elif alert_type == "low_credit":
                msg = (
                    f"💳 *Crédito Baixo!*\n"
                    f"Conta: *{payload.get('account', '?')}* — {payload.get('pct', '?')}% restante.\n"
                    f"Ação recomendada: {payload.get('action', 'Verificar conta')}"
                )
                await self._send_whatsapp_alert("warning", msg)

        elif topic == "job.failed":
            msg = (
                f"❌ *Job Falhou!*\n"
                f"Job ID: `{str(payload.get('job_id', '?'))[:8]}...`\n"
                f"Conta: {payload.get('account_label', '?')}\n"
                f"Erro: {payload.get('error', 'Desconhecido')}"
            )
            await self._send_whatsapp_alert("warning", msg)

    def _read_json(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.memory_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[Maestro] Erro ao ler {filename}: {e}")
        return {"status": "offline", "data": {}, "alerts": ["Agente offline ou arquivo inacessível."]}

    def get_hive_status(self) -> Dict[str, Any]:
        """Gera o relatório mestre da Colmeia a partir das memórias individuais."""
        status_cerbero  = self._read_json("memory_cerbero.json")
        status_zelador  = self._read_json("memory_zelador.json")
        status_watchdog = self._read_json("memory_watchdog.json")

        global_alerts = []
        global_alerts.extend([f"[Segurança]: {a}" for a in status_cerbero.get("alerts", [])])
        global_alerts.extend([f"[Limpeza]: {a}"   for a in status_zelador.get("alerts", [])])
        global_alerts.extend([f"[Nuvem]: {a}"     for a in status_watchdog.get("alerts", [])])

        return {
            "maestro_status": "online" if self.is_running else "offline",
            "global_alerts": global_alerts,
            "agents": {
                "security":       status_cerbero,
                "infrastructure": status_zelador,
                "cloud_api":      status_watchdog
            }
        }

    async def start_patrol(self):
        """O Loop de Consciência e Proatividade do Maestro."""
        self.is_running = True
        logger.info("🧠 [Maestro] Loop de Consciência ativado. Maestro operando com vida própria.")
        self.update_memory("status", "conscious")

        while self.is_running:
            try:
                await self._reflect_and_act()
                self.memory_data["last_action"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                # Avalia a colmeia a cada 1 hora
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"[Maestro] Falha no Loop de Consciência: {e}")
                await asyncio.sleep(300)

    async def _reflect_and_act(self):
        """Usa a Inteligência Central para avaliar a colmeia e decidir se deve agir."""
        hive_status = self.get_hive_status()
        logger.info("🧠 [Maestro] Refletindo sobre o estado da colmeia...")

        prompt = f"""
        Você é o MAESTRO, o Agente de IA Gerente do sistema Apollo.
        Supervisione os outros agentes (Zelador, Cérbero, Watchdog) e o estado do servidor.

        Relatório atual da colmeia:
        {json.dumps(hive_status, indent=2)}

        Existe algum ALERTA CRÍTICO que exige atenção imediata do CEO?
        Exemplos: falta de chaves API, disco baixo, ataques de segurança, contas offline.

        Se NORMAL e ESTÁVEL, responda APENAS: "TUDO_BEM".
        Se houver algo crítico, escreva UMA MENSAGEM CURTA para o CEO (como um WhatsApp real).
        Sem markdown, apenas texto puro.
        """

        response = await self.router.request_ai_generation(
            prompt=prompt,
            system_prompt="Você é um gerente de TI autônomo, direto e eficiente."
        )

        if response.get("status") == "success":
            decision = response["content"].strip()
            if "TUDO_BEM" not in decision:
                logger.warning("🚨 [Maestro] Enviando mensagem proativa ao CEO!")
                await self._send_whatsapp_alert("critical", decision)

                if "messages_sent" not in self.memory_data["data"]:
                    self.memory_data["data"]["messages_sent"] = []
                self.memory_data["data"]["messages_sent"].append({
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "message": decision
                })
            else:
                logger.info("🧠 [Maestro] Sistema estável. Nenhuma ação necessária.")

    async def _send_whatsapp_alert(self, level: str, message: str):
        """Envia alerta ao CEO via WhatsApp Bridge."""
        logger.info(f"📱 [WhatsApp OUT] [{level.upper()}] {message[:80]}...")
        success = await whatsapp_bridge.send_alert(level, message)
        if not success:
            logger.warning("[Maestro] Bridge WhatsApp offline ou CEO_WHATSAPP_NUMBER não configurado.")

    async def process_ceo_command(self, text: str) -> str:
        """
        Processa comandos recebidos via WhatsApp pelo CEO.
        Retorna a resposta em texto para ser enviada de volta.
        """
        text_lower = text.lower().strip()

        if "status" in text_lower or "como vai" in text_lower:
            hive = self.get_hive_status()
            n_alerts = len(hive.get("global_alerts", []))
            status_str = "✅ Tudo funcionando." if n_alerts == 0 else f"⚠️ {n_alerts} alerta(s) ativo(s)."
            return (
                f"🤖 *Apollo Status Report*\n"
                f"Maestro: {'Online' if hive['maestro_status'] == 'online' else 'Offline'}\n"
                f"{status_str}\n"
                f"Alertas: {', '.join(hive['global_alerts']) if n_alerts else 'Nenhum'}"
            )

        elif "pool" in text_lower or "contas" in text_lower:
            from backend.cloud_tools.account_pool import account_pool
            accounts = account_pool.status_report()
            lines = ["🔍 *Pool de Contas Lightning:*"]
            for a in accounts:
                icon = "🟢" if a["is_healthy"] else "🔴"
                lines.append(f"{icon} {a['label']}: {a['jobs_today']} jobs hoje")
            return "\n".join(lines)

        elif "ajuda" in text_lower or "help" in text_lower:
            return (
                "🧠 *Comandos Apollo disponíveis:*\n"
                "- *status* — Saúde geral do sistema\n"
                "- *pool* / *contas* — Pool de contas Lightning\n"
                "- *ajuda* / *help* — Esta mensagem\n"
                "Ou faça qualquer pergunta livremente!"
            )

        else:
            # Responde via LLM para perguntas livres
            response = await self.router.request_ai_generation(
                prompt=f"O CEO do Apollo mandou esta mensagem pelo WhatsApp: '{text}'\nResponda de forma curta e útil em português.",
                system_prompt="Você é o Maestro, gerente de TI do Apollo. Seja direto e útil."
            )
            return response.get("content", "Não consegui processar sua mensagem.").strip()
