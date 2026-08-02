from .provider_r2 import CloudflareR2Provider
from .provider_oci import OracleOCIProvider
from .provider_telegram import TelegramBotProvider

class StorageRouter:
    """
    Roteador de armazenamento. Decide para qual provedor o arquivo será enviado
    com base no tamanho e tipo, evitando custos de egress.
    """
    
    def __init__(self):
        self.r2_provider = CloudflareR2Provider()
        self.oci_provider = OracleOCIProvider()
        self.telegram_provider = TelegramBotProvider()
        
        self.providers = {
            "cloudflare_r2": self.r2_provider,
            "oracle_oci": self.oci_provider,
            "telegram_bot": self.telegram_provider
        }

    async def upload_inteligente(self, file_bytes: bytes, file_name: str, content_type: str) -> dict:
        """
        Lógica baseada em FinOps:
        - Tamanho < 5MB (geralmente Imagens) -> R2 (Cloudflare Zero Egress)
        - Tamanho 5MB - 50MB (geralmente Vídeos) -> OCI (Oracle 10TB Egress)
        """
        size_bytes = len(file_bytes)
        size_mb = size_bytes / (1024 * 1024)
        
        provider_escolhido = None
        
        if size_mb < 5.0:
            provider_escolhido = self.r2_provider
        else:
            provider_escolhido = self.oci_provider
            
        # Tenta enviar para o provider primário
        try:
            url_interna = await provider_escolhido.put_object(file_bytes, file_name, content_type)
            return {
                "provider": provider_escolhido.get_provider_name(),
                "provider_url": url_interna
            }
        except Exception as e:
            print(f"Fallback! Erro no provedor {provider_escolhido.get_provider_name()}: {e}")
            # Fallback para o Telegram Bot (Storage Frio/Overflow)
            try:
                url_interna = await self.telegram_provider.put_object(file_bytes, file_name, content_type)
                return {
                    "provider": self.telegram_provider.get_provider_name(),
                    "provider_url": url_interna
                }
            except Exception as e2:
                raise Exception(f"Falha Catastrófica em todos os Provedores. Erro: {e2}")

    def get_public_redirect_url(self, provider_name: str, provider_url: str) -> str:
        """
        Dado o provedor e a URL interna, retorna o link HTTP de redirecionamento.
        """
        if provider_name not in self.providers:
            raise ValueError(f"Provedor {provider_name} desconhecido.")
            
        provider = self.providers[provider_name]
        return provider.get_public_url(provider_url)
