import json
import re
import requests
import time
import logging

class XTTSDynamicRoteirista:
    """
    Pré-processador de texto para o XTTSv2.
    Lê o roteiro bruto e o divide em fatias semânticas carimbadas com emoção, arousal e pace
    utilizando a inteligência do Gemini (ou outro LLM).
    """
    
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.api_keys = self._load_gemini_keys()
        
    def _load_gemini_keys(self):
        valid_keys = []
        if self.config_manager:
            try:
                keys = self.config_manager.get_api_config("gemini", "api_keys")
                if isinstance(keys, list):
                    for item in keys:
                        k = None
                        if isinstance(item, dict):
                            k = item.get("key", "").strip()
                        elif isinstance(item, str):
                            k = item.strip()
                        if k and k != "YOUR_API_KEY" and k not in valid_keys:
                            valid_keys.append(k)
                if not valid_keys:
                    single = self.config_manager.get_api_config("gemini", "api_key")
                    if isinstance(single, str) and single.strip() and single.strip() != "YOUR_API_KEY":
                        valid_keys.append(single.strip())
            except Exception as e:
                logging.warning(f"[XTTS-Roteirista] Erro ao carregar chaves: {e}")
        return valid_keys
        
    def fatiar_texto(self, text: str, fallback_emotion: str = "neutral"):
        """
        Divide o texto usando LLM e retorna uma lista de dicionários.
        Ex: [{"text": "...", "emotion": "neutral", "arousal": "medium", "pace": "normal"}]
        Se a IA falhar, retorna o texto inteiro como um bloco neutro (fallback seguro).
        """
        # Se o texto for muito curto, não precisa de IA para fatiar, assume o fallback
        if len(text.strip().split()) < 3 or not self.api_keys:
            return [{"text": text, "emotion": fallback_emotion, "arousal": "medium", "pace": "normal"}]
            
        prompt = f"""
Você é um diretor de dublagem profissional. Seu trabalho é pegar o roteiro abaixo e dividi-lo em pequenas fatias semânticas (frases ou orações).
Para CADA fatia, você deve definir:
1. emotion: A emoção principal. Escolha EXATAMENTE uma das opções: "neutral", "angry", "sad", "ironic".
2. arousal: A intensidade da emoção. Escolha EXATAMENTE uma das opções: "low", "medium", "high".
3. pace: O ritmo da fala. Escolha EXATAMENTE uma das opções: "slow", "normal", "fast".

Regras:
- Não omita nenhuma palavra do texto original. O texto das fatias concatenado deve ser igual ao original.
- Divida onde a emoção ou o ritmo claramente mudam (ex: pontuações, exclamações, perguntas).
- Se for uma frase neutra informativa, use neutral/medium/normal.

Texto:
\"\"\"
{text}
\"\"\"

Responda APENAS com um JSON válido (Array de Objetos), sem nenhum markdown adicional.
Exemplo:
[
  {{"text": "O conselho aprovou a fusão.", "emotion": "neutral", "arousal": "medium", "pace": "normal"}},
  {{"text": "Mas que absurdo! Vocês acham que somos palhaços?!", "emotion": "angry", "arousal": "high", "pace": "fast"}}
]
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        
        for attempt in range(2):
            for key in self.api_keys:
                url = f"{self.GEMINI_BASE_URL}?key={key}"
                try:
                    resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
                    if resp.status_code == 200:
                        data = resp.json()
                        resposta_txt = data["candidates"][0]["content"]["parts"][0]["text"]
                        
                        # Limpar possíveis crases de markdown
                        res_limpa = re.sub(r'```(?:json)?\s*|\s*```', '', resposta_txt).strip()
                        blocos = json.loads(res_limpa)
                        if isinstance(blocos, list) and len(blocos) > 0:
                            return blocos
                    elif resp.status_code == 429:
                        logging.warning("[XTTS-Roteirista] Limite da chave Gemini atingido. Tentando próxima.")
                        continue
                except Exception as e:
                    logging.warning(f"[XTTS-Roteirista] Erro na requisição LLM: {e}")
            time.sleep(1)
            
        # Fallback seguro caso tudo falhe
        logging.error("[XTTS-Roteirista] Falha total ao acionar LLM. Aplicando fallback de texto único.")
        return [{"text": text, "emotion": fallback_emotion, "arousal": "medium", "pace": "normal"}]
