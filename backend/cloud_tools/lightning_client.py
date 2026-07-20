import logging
from typing import Dict, Any, Optional
from .fleet_balancer import fleet_balancer

logger = logging.getLogger("LightningClient")
logger.setLevel(logging.INFO)

class LightningClient:
    def __init__(self):
        # O URL mudará dinamicamente baseado na conta e no studio ativo
        self.active_studio_url = None

    def start_studio(self) -> bool:
        """
        Inicia a máquina (Studio) na Lightning AI usando a chave ativa.
        (A ser integrado com o Lightning AI SDK ou chamadas HTTP diretas).
        """
        account = fleet_balancer.get_lightning_account()
        if not account:
            logger.error("[LightningClient] Não há contas ativas para iniciar a máquina.")
            return False
            
        logger.info(f"[LightningClient] Iniciando Studio na conta: {account['id']} ({account['email']})")
        # Aqui ficará a lógica real de boot do Studio
        self.active_studio_url = f"https://studio-{account['id']}.lightning.ai"
        return True

    def stop_studio(self) -> bool:
        """
        Desliga a máquina para economizar os créditos de $15/mês.
        """
        logger.info("[LightningClient] Desligando Studio para preservar créditos...")
        self.active_studio_url = None
        return True

    async def generate_tts(self, text: str, voice_id: str) -> Dict[str, Any]:
        """
        Exemplo de chamada para inferência leve (Cérebro).
        Se a máquina estiver desligada, ele liga, gera o TTS e devolve.
        """
        if not self.active_studio_url:
            success = self.start_studio()
            if not success:
                return {"status": "error", "message": "Falha ao iniciar o Cérebro na Lightning AI."}
                
        logger.info(f"[LightningClient] Gerando TTS na máquina: {self.active_studio_url}")
        # Simulando uma requisição HTTP para o LLM/TTS hospedado na Lightning
        
        # Se um erro de "Out of Credits" ou "Billing Exceeded" for retornado pela Lightning API:
        # fleet_balancer.mark_exhausted("lightning", account["id"])
        # E repetimos o ciclo.
        
        return {"status": "success", "audio_url": "dummy_audio.mp3"}

lightning_client = LightningClient()
