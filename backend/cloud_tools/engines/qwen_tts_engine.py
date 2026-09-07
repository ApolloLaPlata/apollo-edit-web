import modal
import sys
import os
import time
import base64
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Imagem Modal otimizada para o Qwen3-TTS (Python nativo)
qwen_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libsndfile1", "ffmpeg", "wget")
    .pip_install(
        "torch==2.4.0",
        "torchvision==0.19.0",
        "torchaudio==2.4.0",
        extra_options="--extra-index-url https://download.pytorch.org/whl/cu121"
    )
    .pip_install("hf-transfer", "transformers", "accelerate>=0.33.0", "huggingface_hub")
    .pip_install("soundfile", "scipy", "librosa")
    .pip_install("qwen-tts")
    .env({
        "HF_HUB_ENABLE_HF_TRANSFER": "1"
    })
)

apollo_volume = modal.Volume.from_name("apollo-qwen-volume", create_if_missing=True)
from backend.cloud_tools.modal_app import app

@app.cls(image=qwen_image, gpu="A10G", timeout=600, volumes={"/apollo_volume": apollo_volume}, enable_memory_snapshot=True)
class QwenTtsEngine:
    @modal.enter(snap=True)
    def load_model(self):
        print("[QwenTtsEngine] Baixando/Carregando os pesos do Qwen3-TTS-1.7B-CustomVoice...")
        import torch
        from qwen_tts import Qwen3TTSModel
        
        t0 = time.time()
        self.model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", 
            device_map="cuda:0"
        )
        print(f"[QwenTtsEngine] Modelo carregado na GPU em {time.time() - t0:.2f} segundos!")

    @modal.method()
    def generate(self, text: str, language: str = "Portuguese", speaker: str = "Eric", instruct: str = "") -> dict:
        print(f"[QwenTtsEngine] Gerando áudio para o speaker '{speaker}', língua '{language}'...")
        t0 = time.time()
        import soundfile as sf
        import traceback
        
        try:
            wavs, sr = self.model.generate_custom_voice(
                text=text,
                language=language,
                speaker=speaker,
                instruct=instruct
            )
            
            # Converter o array numpy (wavs[0]) para WAV em memória e em seguida Base64
            buffer = io.BytesIO()
            sf.write(buffer, wavs[0], sr, format='WAV')
            audio_bytes = buffer.getvalue()
            b64_out = base64.b64encode(audio_bytes).decode("utf-8")
            
            return {
                "status": "success",
                "audio_base64": b64_out,
                "render_time_seconds": round(time.time() - t0, 2)
            }
            
        except Exception as e:
            err = traceback.format_exc()
            return {"status": "error", "message": str(e), "traceback": err}
