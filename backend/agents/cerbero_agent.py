import logging
import asyncio
import time
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger("CerberoAgent")

class CerberoAgent(BaseAgent):
    """
    Agente Autônomo de Segurança (O Cão de Guarda do Firewall).
    Aba do Painel: Segurança
    """
    def __init__(self):
        super().__init__(agent_name="Cerbero")
        
        # Garante as chaves no JSON
        if "blocked_ips" not in self.memory_data["data"]:
            self.memory_data["data"]["blocked_ips"] = []
            self.save_memory()

    async def start_patrol(self):
        self.is_running = True
        logger.info("🐕 [Cérbero] Iniciando patrulha de segurança...")
        self.update_memory("status", "patrolling")
        
        while self.is_running:
            try:
                # Simulação: Análise de Logs a cada 60s
                await asyncio.sleep(60)
                
                # Apenas atualizando o timestamp da última ação para o painel
                self.update_memory("last_action", time.strftime("%Y-%m-%d %H:%M:%S"))
                
            except Exception as e:
                logger.error(f"[Cérbero] Erro na patrulha: {e}")
                self.update_memory("status", "error")
                await asyncio.sleep(60)
                
    def ban_ip(self, ip_address: str, reason: str):
        logger.warning(f"🚫 [Cérbero] Banindo IP {ip_address}! Motivo: {reason}")
        
        # Adiciona na memória JSON
        self.memory_data["data"]["blocked_ips"].append({"ip": ip_address, "reason": reason})
        self.update_memory("last_action", f"Baniu o IP {ip_address}")
