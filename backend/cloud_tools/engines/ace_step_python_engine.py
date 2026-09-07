import modal
import os
import base64
import time
from backend.cloud_tools.modal_app import app

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "wget")
    .pip_install(
        "torch",
        "torchvision",
        "torchaudio",
        extra_options="--index-url https://download.pytorch.org/whl/cu124"
    )
    .pip_install(
        "transformers",
        "accelerate",
        "safetensors",
        "soundfile",
        "pydub",
        "fastapi",
        "huggingface_hub"
    )
    .run_commands(
        "git clone https://github.com/ace-step/ACE-Step.git /ace-step",
        "cd /ace-step && sed -i '/flash-attn/d' requirements.txt && pip install -r requirements.txt"
    )
)

volume = modal.Volume.from_name("model-cache-vol", create_if_missing=True)

@app.cls(
    image=image,
    gpu="A10G",
    volumes={"/root/.cache/huggingface": volume},
    timeout=600
)
class AceStepPythonEngine:
    @modal.enter()
    def setup(self):
        import sys
        sys.path.append("/ace-step")
        from huggingface_hub import snapshot_download
        
        print("[AceStepPythonEngine] Baixando/verificando modelo oficial no HuggingFace...")
        self.model_path = snapshot_download(repo_id="ACE-Step/Ace-Step1.5")
        
        print("[AceStepPythonEngine] Carregando pipeline na VRAM...")
        from acestep.pipeline_ace_step import ACEStepPipeline
        self.pipeline = ACEStepPipeline(
            checkpoint_dir=self.model_path,
            dtype="bfloat16",
            torch_compile=False
        )
        print("[AceStepPythonEngine] Pipeline pronto!")

    @modal.method()
    def generate(self, style_tags: str, lyrics: str, length_seconds: int = 30) -> dict:
        t0 = time.time()
        print(f"[AceStepPythonEngine] Gerando áudio de {length_seconds}s...")
        
        import io
        import uuid
        out_file = f"/tmp/ace_{uuid.uuid4().hex}.wav"
        
        try:
            self.pipeline(
                audio_duration=float(length_seconds),
                prompt=style_tags,
                lyrics=lyrics,
                infer_step=50,
                guidance_scale=4.5,
                manual_seeds=[int(time.time())],
                save_path=out_file,
            )
            
            with open(out_file, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
                
            return {
                "status": "success",
                "audio_base64": audio_b64,
                "render_time_seconds": round(time.time() - t0, 2)
            }
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
