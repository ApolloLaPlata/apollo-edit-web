import os
import modal

def download_models():
    from modelscope import snapshot_download
    print("Baixando os pesos do CosyVoice2-0.5B na etapa de build...")
    snapshot_download('iic/CosyVoice2-0.5B')

cosy_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "sox", "libsox-dev", "build-essential")
    .run_commands(
        "git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git /workspace/CosyVoice",
        "cd /workspace/CosyVoice && sed -i '/openai-whisper/d' requirements.txt && sed -i '/deepspeed/d' requirements.txt && pip install -r requirements.txt",
        "pip install --no-build-isolation openai-whisper==20231117",
        "pip install modelscope pydantic fastapi ormsgpack"
    )
    .env({"PYTHONPATH": "/workspace/CosyVoice/third_party/Matcha-TTS:/workspace/CosyVoice", "MODELSCOPE_CACHE": "/models/modelscope_cache"})
)

try:
    from backend.cloud_tools.modal_app import app
except ImportError:
    app = modal.App("apollo-api-cosyvoice", image=cosy_image)

vol = modal.Volume.from_name("apollo-voice-models", create_if_missing=True)

@app.cls(gpu="L4", scaledown_window=120, image=cosy_image, volumes={"/models": vol})
class CosyVoiceEngine:
    @modal.enter()
    def setup(self):
        import sys
        sys.path.insert(0, "/workspace/CosyVoice/third_party/Matcha-TTS")
        sys.path.insert(0, "/workspace/CosyVoice")
        from cosyvoice.cli.cosyvoice import CosyVoice2
        from modelscope import snapshot_download
        
        print("Downloading CosyVoice2-0.5B...")
        model_dir = snapshot_download('iic/CosyVoice2-0.5B', cache_dir='/models/modelscope_cache')
        print("Loading CosyVoice2...")
        # Note: CosyVoice2-0.5B model
        self.cosyvoice = CosyVoice2(model_dir, load_jit=False, load_trt=False, fp16=True)
        print("CosyVoice2 Loaded.")

    @modal.method()
    def generate_voice(self, tts_text: str, instruct_text: str, prompt_text: str, reference_audio_bytes: bytes):
        import torchaudio
        import io
        import tempfile
        import torch
        from cosyvoice.utils.file_utils import load_wav
        
        # Load reference audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(reference_audio_bytes)
            tmp_path = tmp.name
            
        # In CosyVoice2, zero-shot with instruct uses <|endofprompt|> in the tts_text
        if instruct_text:
            full_tts_text = f"{instruct_text}<|endofprompt|>{tts_text}"
        else:
            full_tts_text = tts_text
            
        print(f"[CosyVoiceEngine] Generating Zero-Shot for: {full_tts_text}")
        
        # In CosyVoice2 the argument expects a file path directly (which is passed to load_wav internally)
        output = self.cosyvoice.inference_zero_shot(
            full_tts_text,
            prompt_text,
            tmp_path
        )
        
        audio_chunks = []
        for i, j in enumerate(output):
            audio_chunks.append(j['tts_speech'])
            
        final_audio = torch.cat(audio_chunks, dim=1)
        
        out_buf = io.BytesIO()
        torchaudio.save(out_buf, final_audio, self.cosyvoice.sample_rate, format="wav")
        
        os.remove(tmp_path)
        return out_buf.getvalue()
