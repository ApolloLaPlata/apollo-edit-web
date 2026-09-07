import base64
import time
import io
import os
import torch
import soundfile as sf
import traceback
import tempfile
from qwen_tts import Qwen3TTSModel

class QwenTtsLocalEngine:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        print("[QwenTtsLocalEngine] Carregando modelo Qwen3-TTS localmente na GPU...")
        t0 = time.time()
        import torch
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-Base", 
            torch_dtype=torch.bfloat16,
            device_map=device
        )
        print(f"[QwenTtsLocalEngine] Modelo Base carregado em {time.time() - t0:.2f} segundos!")

    def clone(self, text: str, ref_audio_path: str, ref_text: str, language: str = "Portuguese", instruct: str = "", temperature: float = 1.0) -> dict:
        print(f"[QwenTtsLocalEngine] Iniciando clonagem (Language: {language})...")
        t0 = time.time()
        
        try:
            kwargs = {"temperature": temperature}
            if instruct:
                kwargs["instruct"] = instruct

            wavs, sr = self.model.generate_voice_clone(
                text=text,
                language=language,
                ref_audio=ref_audio_path,
                ref_text=ref_text,
                **kwargs
            )
            
            buffer = io.BytesIO()
            sf.write(buffer, wavs[0], sr, format='WAV')
            out_bytes = buffer.getvalue()
            b64_out = base64.b64encode(out_bytes).decode("utf-8")
            
            return {
                "status": "success",
                "audio_base64": b64_out,
                "render_time_seconds": round(time.time() - t0, 2)
            }
            
        except Exception as e:
            err = traceback.format_exc()
            return {"status": "error", "message": str(e), "traceback": err}
