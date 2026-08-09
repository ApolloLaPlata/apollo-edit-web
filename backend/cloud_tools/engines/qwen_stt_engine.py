"""
Motor STT Qwen3-ASR via Modal
=============================================
Modelo ASR SOTA em benchmarks de transcrição, superando o Whisper em precisão bruta.
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import tempfile
from fastapi import Request

MODEL_ID = "Qwen/Qwen2-Audio-7B-Instruct"

qwen_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "torch>=2.0.0",
        "torchaudio",
        "transformers>=4.43.0",
        "accelerate",
        "librosa",
        "fastapi",
        "python-multipart",
        "tiktoken",
        "protobuf"
    )
)

@app.cls(
    image=qwen_image,
    gpu="L4",
    timeout=300,
    min_containers=0,
    enable_memory_snapshot=True,
    volumes={"/data": modal.Volume.from_name("apollo-voice-models")},
)
class QwenSTT:
    def __init__(self):
        self.model = None
        self.processor = None
        self.model_path = "/data/Qwen2-Audio-7B-Instruct"

    @modal.enter()
    def load_model(self):
        import torch
        print(f"Preloading {MODEL_ID} for STT from local volume...")
        
        if not torch.cuda.is_available():
            print("Snapshot Build: Lendo os pesos da RAM via Volume local...")
            from transformers import AutoProcessor, AutoModelForCausalLM
            if os.path.exists(self.model_path):
                _ = AutoProcessor.from_pretrained(self.model_path, trust_remote_code=True)
                _ = AutoModelForCausalLM.from_pretrained(self.model_path, trust_remote_code=True)
                print("Pesos do Qwen ASR carregados para RAM!")
            else:
                print("ERRO: Pesos não encontrados no Volume Local.")

    @modal.method()
    def transcribe_audio_bytes(self, audio_bytes: bytes) -> str:
        import torch
        from transformers import AutoProcessor, AutoModelForCausalLM
        import librosa

        if self.processor is None:
            print("First request: Instanciando Qwen ASR na GPU...")
            path_to_load = self.model_path if os.path.exists(os.path.join(self.model_path, "config.json")) else MODEL_ID
            print(f"Loading weights from: {path_to_load}")
            self.processor = AutoProcessor.from_pretrained(path_to_load, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(path_to_load, trust_remote_code=True).to("cuda").eval()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            f.flush()
            temp_path = f.name
            
        try:
                
            text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            # Remove o prompt inicial da resposta
            text = text.replace("Transcribe the audio to text:", "").strip()
            return text
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

@app.function(image=qwen_image)
@modal.fastapi_endpoint(method="POST", label="apollo-api-qwen-stt")
async def api_qwen_stt(request: Request):
    try:
        from fastapi import UploadFile, Request
        form = await request.form()
        if "file" not in form:
            return JSONResponse({"error": "Nenhum arquivo enviado"}, status_code=400)
            
        file: UploadFile = form["file"]
        audio_bytes = await file.read()
        
        stt_service = QwenSTT()
        text = await stt_service.transcribe_audio_bytes.remote.aio(audio_bytes)
        return {"text": text}
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
