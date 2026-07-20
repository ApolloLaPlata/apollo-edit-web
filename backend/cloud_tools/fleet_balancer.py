import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("FleetBalancer")
logger.setLevel(logging.INFO)

class FleetBalancer:
    def __init__(self, config_path: str = "backend/cloud_tools/fleet_secrets.json"):
        # Resolve path relative to the project root
        if not os.path.isabs(config_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.config_path = os.path.join(base_dir, config_path)
        else:
            self.config_path = config_path
            
        self.fleet_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            logger.error(f"[Fleet] Arquivo de configuração não encontrado: {self.config_path}")
            return {"lightning_accounts": [], "modal_accounts": []}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[Fleet] Erro ao carregar frota: {str(e)}")
            return {"lightning_accounts": [], "modal_accounts": []}

    def _save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.fleet_data, f, indent=2)
            logger.info("[Fleet] Arquivo de frota atualizado com sucesso.")
        except Exception as e:
            logger.error(f"[Fleet] Erro ao salvar frota: {str(e)}")

    def get_modal_account(self) -> Optional[Dict[str, str]]:
        """Retorna a primeira conta Modal com status 'active'."""
        for acc in self.fleet_data.get("modal_accounts", []):
            if acc.get("status") == "active":
                logger.info(f"[Fleet] Roteando para Modal: {acc['id']}")
                return acc
        logger.error("[Fleet] ALERTA CRÍTICO: Todas as contas da Modal estão esgotadas ou pendentes!")
        return None

    def get_lightning_account(self) -> Optional[Dict[str, str]]:
        """Retorna a primeira conta Lightning com status 'active'."""
        for acc in self.fleet_data.get("lightning_accounts", []):
            if acc.get("status") == "active":
                logger.info(f"[Fleet] Roteando para Lightning: {acc['id']}")
                return acc
        logger.error("[Fleet] ALERTA CRÍTICO: Todas as contas da Lightning estão esgotadas ou pendentes!")
        return None

    def mark_exhausted(self, provider: str, account_id: str):
        """
        Marca uma conta como esgotada (out_of_credits).
        Isso forçará a próxima requisição a usar a chave subsequente.
        """
        key = "modal_accounts" if provider.lower() == "modal" else "lightning_accounts"
        
        for acc in self.fleet_data.get(key, []):
            if acc.get("id") == account_id:
                acc["status"] = "exhausted"
                logger.warning(f"[Fleet] Conta {account_id} do provedor {provider} marcada como ESGOTADA.")
                self._save_config()
                return
        logger.error(f"[Fleet] Falha ao marcar conta: {account_id} não encontrada em {provider}.")

# Instância global Singleton para ser importada por outros módulos
fleet_balancer = FleetBalancer()
