import os
import requests
import json
import base64

class FishSpeechEngine:
    """
    Cliente para a API do Fish Speech.
    Como o Fish Speech é pesado, a recomendação (via Perplexity) é rodá-lo 
    localmente via Docker (docker compose --profile webui up) ou em uma VPS.
    """
    def __init__(self, api_url="http://localhost:8080"):
        # URL base da API do Fish Speech WebUI/Server
        self.api_url = api_url.rstrip("/")

    def generate_emotional_take(self, text: str, emotion_tags: str, reference_audio_path: str, output_path: str) -> bool:
        """
        Gera um take curto e visceral usando a voz clonada do reference_audio_path.
        O texto final será a junção das tags emocionais com o texto.
        Ex: text="D'OH!!!", emotion_tags="(furious) (shouting)"
        """
        try:
            print(f"🐟 [FishSpeechEngine] Gerando take para tags: {emotion_tags}")
            
            # Constrói o texto com os marcadores na frente (sintaxe do Fish Speech)
            full_prompt = f"{emotion_tags} {text}"
            
            if not os.path.exists(reference_audio_path):
                raise FileNotFoundError(f"Áudio base não encontrado: {reference_audio_path}")
                
            # Lógica de conexão (pode variar conforme a versão da API do fish-speech dockerizada)
            files = {
                'reference_audio': open(reference_audio_path, 'rb')
            }
            data = {
                'text': full_prompt,
                'format': 'wav'
            }
            
            try:
                response = requests.post(f"{self.api_url}/v1/tts", files=files, data=data, timeout=120)
                
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    return True
                else:
                    print(f"❌ [FishSpeechEngine] Erro na API do Fish: {response.status_code} - {response.text}")
                    return False
            except requests.exceptions.ConnectionError:
                print(f"⚠️ [FishSpeechEngine] Servidor Fish Speech offline em {self.api_url}.")
                return False
                
        except Exception as e:
            print(f"❌ [FishSpeechEngine] Erro interno: {e}")
            import traceback; traceback.print_exc()
            return False
