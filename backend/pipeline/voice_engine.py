import base64
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

class VoiceEngine:
    def __init__(self):
        self.engine = QwenTtsCloneEngine()
        
    def generate_audio(self, text: str, ref_audio_b64: str, ref_text: str, instruct: str, out_path: str = None, temperature: float = 1.8) -> str:
        """
        Gera o áudio usando o Qwen3-TTS via RPC na Modal.
        Se out_path for fornecido, salva o arquivo e retorna o caminho.
        Caso contrário, retorna o áudio em base64.
        """
        res = self.engine.clone.remote(
            text=text,
            ref_audio_b64=ref_audio_b64,
            ref_text=ref_text,
            language="Portuguese",
            instruct=instruct,
            temperature=temperature
        )
        audio_b64 = res.get("audio_base64")
        
        if out_path and audio_b64:
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            return out_path
            
        return audio_b64
