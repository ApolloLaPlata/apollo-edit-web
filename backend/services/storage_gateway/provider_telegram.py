import os
import httpx
from typing import Dict, Any
from .base_provider import StorageProvider

class TelegramBotProvider(StorageProvider):
    def __init__(self):
        # Credenciais via variavel de ambiente
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "mock_token")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "mock_chat_id")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def get_provider_name(self) -> str:
        return "telegram_bot"

    async def put_object(self, file_bytes: bytes, file_name: str, content_type: str) -> str:
        """
        Envia o arquivo para um chat privado no Telegram.
        Retorna o 'file_id' interno gerado pelo Telegram.
        """
        url = f"{self.api_url}/sendDocument"
        files = {"document": (file_name, file_bytes, content_type)}
        data = {"chat_id": self.chat_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, files=files)
            response.raise_for_status()
            json_response = response.json()
            
            if json_response.get("ok"):
                # Captura o file_id do documento
                document = json_response["result"].get("document")
                if document:
                    file_id = document["file_id"]
                    return f"tg://{file_id}"
            
            raise Exception(f"Erro ao fazer upload no Telegram: {json_response}")

    def get_public_url(self, file_id_or_url: str) -> str:
        """
        Aviso: Esta função é complexa no Telegram, pois o 'file_path' expira rápido.
        Para resolver isso corretamente via Gateway, o Gateway deveria usar httpx
        para pegar o link de download exato antes do redirect.
        """
        file_id = file_id_or_url.replace("tg://", "")
        # O ideal aqui é chamar o getFile do Telegram, mas como get_public_url é síncrona na Interface,
        # retornamos um pseudo-endpoint no próprio Gateway que resolve o getFile de forma assíncrona.
        # Ex: https://api.apolloedit.com/media/tg_resolve/{file_id}
        
        custom_domain = os.environ.get("GATEWAY_PUBLIC_DOMAIN", "https://api.mock-apolloedit.com")
        return f"{custom_domain}/media/tg_resolve/{file_id}"

    async def get_quota_state(self) -> Dict[str, Any]:
        # Telegram é "Ilimitado" para efeitos práticos de armazenamento de bots, mas sujeito a rate limits
        return {
            "storage_used_bytes": 0, 
            "storage_limit_bytes": -1, # Infinito
            "egress_limit_bytes": -1 # Infinito (mas com throttling)
        }

    async def delete_object(self, file_id_or_url: str) -> bool:
        # Deletar mensagens antigas no Telegram para limpar a bagagem.
        # Precisaria salvar o message_id também. Para simplificar, retornamos True (Ignorado).
        return True
