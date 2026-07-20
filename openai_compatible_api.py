import requests
import json
from typing import Optional

class OpenAICompatibleAPI:
    """Cliente genérico para APIs no padrão OpenAI (OpenRouter, Grok, DeepSeek, etc)"""
    
    def __init__(self, base_url: str, api_key: str, model: str, name: str = "Unknown"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.name = name

    def generate_content(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        if not self.api_key:
            print(f"❌ API Key do provedor {self.name} não configurada.")
            return None
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        url = f"{self.base_url}/chat/completions"
        
        try:
            print(f"🤖 [Cascade] Tentando gerar via {self.name} (Modelo: {self.model})...")
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    text = data["choices"][0].get("message", {}).get("content", "")
                    return text
            else:
                print(f"⚠️ [Cascade] Falha na API {self.name} ({response.status_code}): {response.text}")
                return None
                
        except Exception as e:
            print(f"⚠️ [Cascade] Exceção na API {self.name}: {e}")
            return None
            
        return None
