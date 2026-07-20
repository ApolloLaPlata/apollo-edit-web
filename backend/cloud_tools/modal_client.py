import aiohttp
import logging
from typing import Dict, Any
from .fleet_balancer import fleet_balancer

logger = logging.getLogger("ModalClient")
logger.setLevel(logging.INFO)

class ModalClient:
    def __init__(self):
        # Esta URL será atualizada quando fizermos o 'modal deploy'
        self.base_webhook_url = "https://canaltutorialdascoisas--apollo-render-router.modal.run"

    async def call_webhook(self, endpoint: str, payload: Dict[str, Any], max_retries=3) -> Dict[str, Any]:
        """
        Chama um webhook na Modal usando a chave ativa.
        Se receber erro de limite de créditos, roda a chave e tenta de novo.
        """
        for attempt in range(max_retries):
            account = fleet_balancer.get_modal_account()
            if not account:
                return {"status": "error", "message": "Nenhuma conta Modal ativa disponível na frota."}
            
            headers = {
                "Content-Type": "application/json",
                # O Header Modal-Key e Modal-Secret protege nosso endpoint contra uso não autorizado
                "Modal-Key": account.get("proxy_id", ""),
                "Modal-Secret": account.get("proxy_secret", "")
            }
            
            url = f"{self.base_webhook_url}/{endpoint}"
            logger.info(f"[ModalClient] Chamando {url} com a conta {account['id']} (Tentativa {attempt+1})")
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 402 or "out of credits" in (await response.text()).lower():
                            # Erro clássico de falta de saldo
                            logger.error(f"[ModalClient] Conta {account['id']} sem créditos! Rotacionando chave...")
                            fleet_balancer.mark_exhausted("modal", account["id"])
                            continue # Tenta de novo no próximo loop com a nova chave
                        else:
                            error_text = await response.text()
                            logger.error(f"[ModalClient] Erro HTTP {response.status}: {error_text}")
                            return {"status": "error", "message": error_text, "code": response.status}
            except Exception as e:
                logger.error(f"[ModalClient] Falha de conexão: {str(e)}")
                return {"status": "error", "message": str(e)}
                
        return {"status": "error", "message": "Max retries excedidos. Todas as tentativas falharam."}

modal_client = ModalClient()
