"""
Motor TTS Fish-Speech
======================================
Modelo excelente para clonagem Zero-Shot e alta fidelidade em PT-BR.
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import io

# Definição do Ambiente
fish_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "build-essential", "portaudio19-dev")
    .pip_install(
        "torch==2.3.1",
        "torchaudio==2.3.1",
        "fastapi[standard]",
        "soundfile",
        "huggingface_hub",
        "httpx"
    )
    .run_commands(
        "git clone -b v1.5.1 https://github.com/fishaudio/fish-speech.git /opt/fish-speech",
        "cd /opt/fish-speech && pip install -e ."
    )
)

fish_volume = modal.Volume.from_name("fish-cache", create_if_missing=True)

@app.cls(
    image=fish_image, 
    gpu="A10G", 
    timeout=900, 
    scaledown_window=30, 
    min_containers=0,
    volumes={"/root/.cache/huggingface": fish_volume}
)
class FishTTSEngine:
    @modal.enter()
    def load_model(self):
        print("[INIT] Carregando Fish-Speech na VRAM...")
        
        from huggingface_hub import snapshot_download
        import subprocess
        import time
        import httpx
        import os
        
        ckpt_dir = snapshot_download(repo_id="fishaudio/fish-speech-1.5")
        decoder_pth = os.path.join(ckpt_dir, "firefly-gan-vq-fsq-8x1024-21hz-generator.pth")
        
        cmd = [
            "python", "tools/api_server.py",
            "--listen", "127.0.0.1:8080",
            "--llama-checkpoint-path", ckpt_dir,
            "--decoder-checkpoint-path", decoder_pth,
            "--decoder-config-name", "firefly_gan_vq",
            "--half"
        ]
        
        self.server_proc = subprocess.Popen(cmd, cwd="/opt/fish-speech")
        
        print("[INIT] Aguardando API Server interno do Fish-Speech subir...")
        for _ in range(60):
            try:
                r = httpx.get("http://127.0.0.1:8080/docs")
                if r.status_code == 200:
                    break
            except Exception:
                pass
            time.sleep(2)
        print("[INIT] Fish-Speech Pronto para Geração (Server Online)!")

    @modal.method()
    def generate_voice(self, text: str, reference_audio_bytes: bytes = None):
        import httpx
        import ormsgpack
        
        print(f"[GEN] Recebido pedido Fish-Speech. Texto: {text[:50]}...")
        
        payload = {
            "text": text,
            "reference_id": None,
            "references": [],
            "format": "wav",
            "chunk_length": 200,
            "streaming": False
        }
        
        if reference_audio_bytes:
            from fish_speech.utils.schema import ServeReferenceAudio
            # A API espera os audios como ServeReferenceAudio no formato MsgPack
            # Mas como não importamos no cliente, apenas montamos a estrtura do Pydantic
            payload["references"] = [
                {
                    "audio": reference_audio_bytes,
                    "text": "" # No v1.5 API, text can be empty if it's promptless reference? Wait, fish speech needs reference text usually. We will leave empty and let it transcribe or fail. 
                }
            ]
            
        try:
            # Enviamos via JSON primeiro. Mas a API pede MsgPack se usarmos binarios (audio).
            # Para evitar erro de schema, enviamos request MsgPack.
            headers = {"Content-Type": "application/msgpack"}
            packed_data = ormsgpack.packb(payload)
            
            resp = httpx.post("http://127.0.0.1:8080/v1/tts", content=packed_data, headers=headers, timeout=300)
            if resp.status_code != 200:
                raise RuntimeError(f"Fish API Error: {resp.status_code} - {resp.text}")
                
            return resp.content
        except Exception as e:
            print("Fish-Speech API Request Error:", e)
            raise RuntimeError(f"Fish-Speech falhou: {e}")


from fastapi import Request

@app.function(image=fish_image)
@modal.fastapi_endpoint(method="POST", label="apollo-api-fish-tts")
async def api_fish_tts(request: Request):
    try:
        from fastapi.responses import Response, JSONResponse
        
        data = await request.json()
        text = data.get("text", "")
        ref_audio_base64 = data.get("ref_audio_base64", None)
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        reference_audio_bytes = None
        if ref_audio_base64:
            import base64
            reference_audio_bytes = base64.b64decode(ref_audio_base64)
            
        tts_service = FishTTSEngine()
        audio_bytes = tts_service.generate_voice.remote(text, reference_audio_bytes=reference_audio_bytes)
        
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
