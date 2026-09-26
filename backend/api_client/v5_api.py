import os
import httpx
import logging

logger = logging.getLogger("V5_APOLLO_API_Client")

class V5ApolloAPIClient:
    def __init__(self):
        self.base_url = os.getenv("V5_APOLLO_API_URL", "http://localhost:8000") # Ex: URL da API Central
        self.api_key = os.getenv("V5_APOLLO_MASTER_KEY", "default-dev-key")
        
    async def _post(self, endpoint: str, payload: dict):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                logger.info(f"[API Client] Enviando payload para {url}")
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"[API Client] Erro HTTP {e.response.status_code} em {url}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"[API Client] Erro na comunicação com a API Central: {e}")
            raise

    # ==========================================
    # MÉTODOS DE GERAÇÃO TERCEIRIZADA (ROTEAMENTO)
    # ==========================================

    async def generate_llm(self, system_prompt: str, user_prompt: str, model_id: str = "auto"):
        payload = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "model": model_id
        }
        return await self._post("/api/generate/llm", payload)

    async def generate_tts(self, text: str, voice_id: str, model_id: str = "auto"):
        payload = {
            "text": text,
            "voice_id": voice_id,
            "model": model_id
        }
        return await self._post("/api/generate/tts", payload)

    async def clone_voice(self, audio_sample_url: str, text: str, model_id: str = "auto"):
        payload = {
            "sample_url": audio_sample_url,
            "text": text,
            "model": model_id
        }
        return await self._post("/api/generate/voice_clone", payload)

    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9", model_id: str = "auto"):
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "model": model_id
        }
        return await self._post("/api/generate/image", payload)
        
    async def generate_video(self, prompt: str, image_url: str = None, model_id: str = "auto"):
        payload = {
            "prompt": prompt,
            "image_url": image_url,
            "model": model_id
        }
        return await self._post("/api/generate/video", payload)

api_client = V5ApolloAPIClient()