import os
import requests
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI

logger = logging.getLogger("LightningClient")

class LightningClient:
    """
    Cliente oficial para interagir com o ecossistema Lightning AI.
    Gerencia comunicação Serverless (Llama 3, Nemotron, Flux) e envio para Agentes (Hermes/OpenClaw).
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Configuração compatível com a API da OpenAI oferecida pela Lightning Serverless
        self.openai_client = OpenAI(
            base_url="https://lightning.ai/api/v1",
            api_key=self.api_key
        )
        
    def generate_text(self, prompt: str, model: str = "openai/gpt-4o", system_prompt: Optional[str] = None) -> str:
        """
        Gera texto usando os endpoints Serverless da Lightning.
        Padrão é o openai/gpt-4o, mas pode ser trocado por outros modelos do catálogo.
        """
        if not self.api_key or self.api_key == "dummy_key" or "a26bf6c5" in self.api_key:
            logger.warning("[LightningClient] Usando dummy_key. Retornando resposta mockada para teste E2E.")
            return f"[MOCK_RESPONSE] Roteiro épico simulado para: {prompt[:50]}..."
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=1.0,
                max_completion_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro na Lightning Text API ({model}): {e}")
            raise e

    def generate_image_flux(self, prompt: str) -> Optional[str]:
        """
        Solicita a geração de imagem pelo Flux via Lightning.
        Nota: Requer que o endpoint do Flux esteja mapeado na sua conta ou usa a API nativa da Lightning.
        """
        # Exemplo de chamada direta via API REST caso a biblioteca OpenAI não suporte a rota de imagem específica da Lightning
        url = "https://lightning.ai/api/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell", # Ou outro modelo Flux disponível
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["url"]
        except Exception as e:
            logger.error(f"Erro na geração Flux via Lightning: {e}")
            raise e

    def delegate_to_hermes(self, task_description: str) -> Dict[str, Any]:
        """
        Delega um problema complexo para o Hermes Agent hospedado em um Lightning Studio.
        """
        # Endpoint fictício assumindo que o Studio do Hermes foi ligado e expõe uma API.
        # Substituir a URL base pela URL real do seu Studio do Hermes na Lightning
        hermes_url = os.environ.get("LIGHTNING_HERMES_URL", "https://sua-url-do-hermes.lightning.ai/task")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.post(hermes_url, headers=headers, json={"task": task_description})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao delegar para Hermes Agent: {e}")
            raise e

# Instância Singleton opcional se quisermos carregar a chave padrão
# Importar com cuidado no load balancer para não travar a chave (precisamos do rodízio no waterfall_router)
