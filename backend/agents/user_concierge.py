import logging
import asyncio
import time
from backend.agents.base_agent import BaseAgent
from backend.router.waterfall_router import WaterfallRouter
from backend.api.routes_ui_ws import ui_ws_manager

logger = logging.getLogger("UserConcierge")

class UserConciergeAgent(BaseAgent):
    """
    Agente Focado no Cliente Final (O Concierge).
    Semi-Proativo: Fica observando o comportamento dos usuários no site.
    Se o usuário parece perdido ou precisa de ajuda, o Concierge age.
    """
    def __init__(self, router_instance: WaterfallRouter):
        super().__init__(agent_name="Concierge")
        self.router = router_instance
        
        if "active_sessions" not in self.memory_data["data"]:
            self.memory_data["data"]["active_sessions"] = {}
            self.save_memory()

    async def start_patrol(self):
        self.is_running = True
        logger.info("🛎️ [Concierge] No balcão. Observando a navegação dos usuários...")
        self.update_memory("status", "observing_users")
        
        while self.is_running:
            try:
                await self._observe_and_assist()
                
                self.memory_data["last_action"] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.save_memory()
                
                # Observa o comportamento a cada 5 minutos
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"[Concierge] Erro ao observar usuários: {e}")
                await asyncio.sleep(60)

    async def _observe_and_assist(self):
        """Analisa os logs de sessão (simulados por enquanto) para achar usuários perdidos."""
        # Simulação: O banco de dados indica que um usuário está há 10 min na mesma tela
        simulated_user = {
            "user_id": "client_102",
            "current_page": "/dashboard/generate-script",
            "time_on_page_minutes": 12,
            "actions_taken": 0
        }
        
        if simulated_user["time_on_page_minutes"] > 10 and simulated_user["actions_taken"] == 0:
            logger.info(f"🛎️ [Concierge] Usuário {simulated_user['user_id']} parece perdido. Avaliando abordagem...")
            
            prompt = f"""
            O usuário {simulated_user['user_id']} está na página {simulated_user['current_page']} há {simulated_user['time_on_page_minutes']} minutos sem fazer nada.
            Devo oferecer ajuda no pop-up do site? Escreva uma mensagem amigável e curta de oferecimento de ajuda.
            Se não for necessário, responda TUDO_BEM.
            """
            
            response = await self.router.request_ai_generation(prompt=prompt, system_prompt="Você é um assistente de suporte ao cliente ultra amigável e prestativo.")
            
            if response.get("status") == "success":
                message = response["content"].strip()
                if "TUDO_BEM" not in message:
                    logger.warning(f"🛎️ [Concierge] Disparando Pop-up Proativo para o usuário: '{message}'")
                    # Dispara o pop-up via WebSocket para a interface do site!
                    await ui_ws_manager.send_to_user(
                        user_id=simulated_user['user_id'],
                        message_type="concierge_popup",
                        payload={"message": message, "title": "Precisa de ajuda?"}
                    )
                    await self.speak("user_assistance_offered", {"user": simulated_user['user_id'], "message": message})
