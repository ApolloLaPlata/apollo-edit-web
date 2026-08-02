from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class StorageProvider(ABC):
    """
    Interface base para todos os provedores de armazenamento do Apollo Storage Gateway.
    Qualquer provedor (Cloudflare, Oracle, Telegram, etc) deve implementar essa interface.
    """
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna o nome do provedor (ex: 'cloudflare_r2', 'oracle_oci', 'telegram_bot')."""
        pass

    @abstractmethod
    async def put_object(self, file_bytes: bytes, file_name: str, content_type: str) -> str:
        """
        Faz o upload do arquivo para o provedor.
        Retorna a URL bruta ou o File ID que o provedor usa internamente.
        """
        pass

    @abstractmethod
    def get_public_url(self, file_id_or_url: str) -> str:
        """
        Dada a URL interna ou o ID, retorna o link que o Gateway fará o Redirect (HTTP 302).
        Isso é útil para provedores como Telegram que precisam resolver um File Path antes de exibir.
        """
        pass

    @abstractmethod
    async def get_quota_state(self) -> Dict[str, Any]:
        """
        Retorna o estado atual da conta.
        Ex: {"storage_used_bytes": 1000000, "storage_limit_bytes": 10000000000}
        """
        pass

    @abstractmethod
    async def delete_object(self, file_id_or_url: str) -> bool:
        """
        Deleta o objeto (necessário para limpar arquivos da 'bagagem').
        """
        pass
