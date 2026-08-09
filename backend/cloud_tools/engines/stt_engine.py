"""
Motor de STT (Speech-to-Text) via GPU na Modal
===============================================
Utiliza `faster-whisper` com o modelo `large-v3` ou `large-v3-turbo` 
para transcrição de altíssima velocidade no servidor.
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import io
from fastapi import Request

# Definição da Imagem e Dependências
stt_image = (
    modal.Image.from_registry("nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04", add_python="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "faster-whisper",
        "ffmpeg-python",
        "fastapi[standard]",
        "python-multipart"
    )
)

MODEL_NAME = "large-v3"

with stt_image.imports():
    from faster_whisper import WhisperModel
    from fastapi import Request, File, UploadFile
    from fastapi.responses import JSONResponse
    import tempfile

@app.cls(
    image=stt_image,
    gpu="L4",
    timeout=300,
    scaledown_window=120,
    enable_memory_snapshot=True,
)
class WhisperTurboSTT:
    @modal.enter()
    def load_model(self):
        try:
            print(f"Loading {MODEL_NAME} model for STT on CUDA...")
            self.model = WhisperModel(MODEL_NAME, device="cuda", compute_type="float16")
            print("Model loaded successfully on CUDA!")
        except Exception as e:
            print(f"CUDA not available (Snapshot Build). Downloading model to cache... ({e})")
            from faster_whisper import download_model
            import glob
            model_path = download_model(MODEL_NAME)
            for f in glob.glob(os.path.join(model_path, "*")):
                if os.path.isfile(f):
                    with open(f, "rb") as file_obj:
                        _ = file_obj.read()
            print("Model files successfully cached in RAM!")

    @modal.fastapi_endpoint(method="POST", label="apollo-api-transcribe")
    async def api_transcribe(self, request: Request):
        try:
            from fastapi import UploadFile
            form = await request.form()
            if "file" not in form:
                return JSONResponse({"error": "No file uploaded"}, status_code=400)
                
            file: UploadFile = form["file"]
            audio_bytes = await file.read()
            
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
                f.write(audio_bytes)
                tmp_path = f.name
                
            try:
                # beam_size 5 (Poder Máximo) garante a precisão absoluta exigida pelo usuário.
                segments, info = self.model.transcribe(tmp_path, beam_size=5, language="pt", vad_filter=True)
                text = " ".join([segment.text for segment in segments])
                return {"text": text.strip()}
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            from fastapi.responses import JSONResponse
            return JSONResponse({"error": str(e)}, status_code=500)
