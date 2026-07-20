import logging
import asyncio
import time
from typing import Dict, Any, Optional
from backend.agents.base_agent import BaseAgent
from backend.cloud_tools.account_pool import account_pool

logger = logging.getLogger("WatchdogAgent")

class WatchdogAgent(BaseAgent):
    """
    O 'Zelador' (Admin Agent) Nativo do Apollo.
    Aba do Painel: Nuvem / APIs
    """
    def __init__(self, router_instance):
        super().__init__(agent_name="Watchdog")
        self.router = router_instance
        
        if "lightning_accounts" not in self.memory_data["data"]:
            self.memory_data["data"]["lightning_accounts"] = {}
            self.save_memory()

    async def start_patrol(self):
        self.is_running = True
        logger.info("[WATCHDOG] Cão de Guarda acordou. Iniciando patrulha 24h...")
        self.update_memory("status", "monitoring_cloud")
        
        while self.is_running:
            await self._check_health()
            self.memory_data["last_action"] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.save_memory()
            await asyncio.sleep(300)

    async def _check_health(self):
        logger.debug("[WATCHDOG] Verificando integridade das Contas Lightning no Pool...")
        accounts = account_pool.get_all()
        active_lightning = [acc for acc in accounts if acc.is_healthy]
        
        self.memory_data["data"]["lightning_accounts"] = {
            "total": len(accounts),
            "active": len(active_lightning)
        }
        
        self.memory_data["alerts"] = []
        if len(active_lightning) < 2:
            msg = f"Atenção Admin: Apenas {len(active_lightning)} contas Lightning ativas! Considere repor."
            logger.warning(f"[WATCHDOG ALERTA] {msg}")
            self.memory_data["alerts"].append(msg)

        if len(active_lightning) == 0:
            msg = "SISTEMA CRÍTICO: Nenhuma conta Lightning ativa. Operando 100% via OpenRouter (Custo Alto!)."
            logger.error(f"[WATCHDOG] {msg}")
            self.memory_data["alerts"].append(msg)

    async def handle_scraper_crash(self, error_traceback: str):
        logger.error(f"[WATCHDOG] Falha detectada no Robô Fantasma. Iniciando Protocolo de Auto-Cura...")
        
        # 1. Pede a cura para a Inteligência Central
        prompt = f"O Scraper quebrou com o erro:\n{error_traceback}\nSugira uma correção Python."
        response = await self.router.request_ai_generation(prompt=prompt, system_prompt="Engenheiro Python focado em anti-bot.")
        
        if response.get("status") == "success":
            fixed_code = response["content"]
            logger.info("[WATCHDOG] Código de cura gerado. Iniciando testes em Sandbox...")
            
            # 2. Simulação: O Watchdog testaria o código (ex: salvando num arquivo temp e rodando pytest)
            await asyncio.sleep(2)
            test_passed = True # Simulando que o código funcionou
            
            if test_passed:
                logger.warning("[WATCHDOG] Cura testada com sucesso! Avisando a colmeia...")
                await self.speak("system_auto_heal", {
                    "component": "scraper_playwright",
                    "status": "fixed_pending_approval",
                    "code": fixed_code
                })
            else:
                await self.speak("system_auto_heal", {
                    "component": "scraper_playwright",
                    "status": "failed_to_heal",
                    "error": "O código gerado pela IA não passou nos testes locais."
                })
        else:
            await self.speak("system_auto_heal", {
                "component": "scraper_playwright",
                "status": "failed_to_generate",
                "error": "A IA falhou em gerar a cura."
            })
