import requests
import json
import os
from typing import Optional, Dict, Any
from backend.services.settings_manager import ConfigManager

class ElevenLabsProvider:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        # Obtém a API Key das configs globais ou do ambiente
        self.api_key = self.config.get("elevenlabs_api_key", os.environ.get("ELEVENLABS_API_KEY", ""))
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech"
        
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print("⚠️ [AVISO] API Key do ElevenLabs não configurada. Configure no painel ou via env ELEVENLABS_API_KEY.")
        else:
            print("[OK] ElevenLabs Configurado com sucesso.")

    def generate_tts(self, text: str, voice_id: str, output_path: str, **kwargs) -> bool:
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            print("❌ [ElevenLabs] API Key não configurada! Impossível gerar áudio.")
            return False

        if not voice_id:
            print("❌ [ElevenLabs] ID da voz (voice_id) não fornecido!")
            return False

        url = f"{self.base_url}/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Parâmetros padrão ou extraídos do kwargs (opcionais)
        model_id = kwargs.get("model_id", "eleven_multilingual_v2")
        stability = kwargs.get("stability", 0.5)
        similarity_boost = kwargs.get("similarity_boost", 0.75)
        style = kwargs.get("style", 0.0)
        use_speaker_boost = kwargs.get("use_speaker_boost", True)
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost
            }
        }
        
        print(f"🚀 Enviando texto para ElevenLabs (Voz ID: {voice_id}, Modelo: {model_id})...")
        try:
            response = requests.post(url, json=data, headers=headers, timeout=60)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ [ElevenLabs] Áudio salvo em: {output_path}")
                return True
            else:
                print(f"❌ [ElevenLabs] Erro da API ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"❌ [ElevenLabs] Falha na conexão ou execução: {e}")
            import traceback; traceback.print_exc()
            return False
