import base64
import requests
import time

class VoiceEngine:
    def __init__(self):
        # A URL do Webhook do Qwen TTS na Conta 10 (apollolaplata)
        self.webhook_url = "https://apollolaplata--apollo-api-qwen-tts.modal.run/"
        
    def generate_audio(self, text: str, ref_audio_b64: str, ref_text: str, instruct: str, out_path: str = None, temperature: float = 1.8) -> str:
        """
        Gera o ǭudio usando o Qwen3-TTS via Webhook na Conta 10 (Modal).
        Se out_path for fornecido, salva o arquivo e retorna o caminho.
        Caso contrǭrio, retorna o ǭudio em base64.
        """
        payload = {
            "text": text,
            "reference_audio_base64": ref_audio_b64,
            "reference_text": ref_text,
            "language": "Portuguese",
            "instruct": instruct,
            "temperature": temperature
        }
        
        print(f"[VoiceEngine] Solicitando TTS (Conta 10): {self.webhook_url} ...")
        t0 = time.time()
        
        response = requests.post(self.webhook_url, json=payload, timeout=600)
        
        if response.status_code != 200:
            raise Exception(f"Erro no webhook Qwen TTS (Status {response.status_code}): {response.text}")
            
        # O Webhook retorna o áudio cru (audio/wav)
        audio_bytes = response.content
        
        if out_path:
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            print(f"[VoiceEngine] Audio salvo com sucesso em {time.time() - t0:.2f}s: {out_path}")
            return out_path
            
        return base64.b64encode(audio_bytes).decode("utf-8")
