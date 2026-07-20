"""
Apollo Modal Engine — LTX-Video-2.3-Distilled (Tier 2)
========================================================
Roda em GPU A100 (40GB).
Modelo LTX-2.3 com suporte a Áudio Nativo simultâneo.
Suporta T2V e I2V na mesma pipeline.
"""

import base64
import os
import traceback
import io
from pathlib import Path
import modal

from backend.cloud_tools.modal_app import app
hf_secret = modal.Secret.from_name("huggingface-secret")

MODEL_DIR = "/models/ltx2_distilled"

ltx_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "git")
    .pip_install(
        "torch==2.5.1",
        "torchvision",
        "accelerate>=0.33.0",
        "git+https://github.com/huggingface/diffusers.git",
        "git+https://github.com/huggingface/transformers.git",
        "bitsandbytes",
        "huggingface_hub[hf_transfer]",
        "safetensors",
        "sentencepiece",
        "imageio",
        "imageio-ffmpeg",
        "av",
        "Pillow",
        "soundfile",
        "scipy"
    )
    .env({
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
        "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
    })
    .run_commands(
        [
            "python -c \"from huggingface_hub import snapshot_download; "
            "from pathlib import Path; dst = '/models/ltx2_distilled'; "
            "Path(dst).mkdir(parents=True, exist_ok=True); "
            "print('[BUILD] Downloading diffusers/LTX-2.3-Distilled-Diffusers...'); "
            "snapshot_download("
            "    repo_id='diffusers/LTX-2.3-Distilled-Diffusers', "
            "    local_dir=dst, "
            "    local_dir_use_symlinks=False"
            "); "
            "sf = list(Path(dst).rglob('*.safetensors')); "
            "print(f'[BUILD] OK — {len(sf)} safetensors bakeados na imagem'); \""
        ]
    )
    .env({
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
    })
)

def _round_vae(x: int, mult: int = 32) -> int:
    return max(mult, int(round(x / mult)) * mult)

PRESETS = {
    "pro": {
        "height": _round_vae(720),
        "width": _round_vae(1280),
        "num_inference_steps": 8,
        "fps": 24.0,
    },
    "fast": {
        "height": _round_vae(320),
        "width": _round_vae(576),
        "num_inference_steps": 8,
        "fps": 16.0,
    }
}

@app.cls(gpu="a10g", timeout=1200, image=ltx_image, enable_memory_snapshot=True, experimental_options={"enable_gpu_snapshot": True})
class LTX13BEngine:
    @modal.enter(snap=True)
    def load_model(self):
        import torch
        from diffusers import LTX2Pipeline, LTXVideoTransformer3DModel
        from transformers import BitsAndBytesConfig
        
        torch.set_grad_enabled(False)
        print("[LTXEngine] Carregando LTX2Pipeline com transformer em 8-bit...")
        
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        transformer = LTXVideoTransformer3DModel.from_pretrained(
            MODEL_DIR,
            subfolder="transformer",
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )

        self.pipe_t2v = LTX2Pipeline.from_pretrained(
            MODEL_DIR,
            transformer=transformer,
            torch_dtype=torch.bfloat16,
            local_files_only=True,
        ).to("cuda")
        self.pipe_t2v.vae.enable_slicing()
        self.pipe_t2v.vae.enable_tiling()

    @modal.method()
    def generate(self, prompt: str, image_base64: str = None, duration: int = 5, preset: str = "pro", aspect_ratio: str = "horizontal", seed: int = 42) -> dict:
        import time
        import torch
        from PIL import Image
        from diffusers.utils import export_to_video

        t0 = time.time()
        print(f"[LTXEngine] Request: {prompt[:50]}... | Preset: {preset} | Dur: {duration}s | I2V: {bool(image_base64)} | Formato: {aspect_ratio}")
        
        cfg = PRESETS.get(preset, PRESETS["pro"])
        
        # Ajusta dimensões baseado no formato (Mantém a resolução total aproximada do preset)
        w, h = cfg["width"], cfg["height"]
        if aspect_ratio == "vertical":
            w, h = cfg["height"], cfg["width"]
        elif aspect_ratio == "square":
            avg = _round_vae((w + h) / 2)
            w, h = avg, avg
            
        frame_rate = cfg["fps"]
        num_frames = int(duration * frame_rate) + 1

        generator = torch.Generator(device="cpu").manual_seed(seed)

        try:
            print("[LTXEngine] Limpando VRAM antes de processar o batch...")
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            
            kwargs = {
                "prompt": prompt,
                "negative_prompt": "worst quality, inconsistent motion, blurry, jittery, distorted",
                "width": w,
                "height": h,
                "num_frames": num_frames,
                "num_inference_steps": cfg["num_inference_steps"],
                "generator": generator,
            }
            
            with torch.inference_mode():
                if image_base64:
                    print("[LTXEngine] Gerando vídeo a partir de IMAGEM (I2V)...")
                    from diffusers import LTX2ImageToVideoPipeline
                    pipe_i2v = LTX2ImageToVideoPipeline(**self.pipe_t2v.components)
                    # Use attention slicing to reduce VRAM peaks during 5s generation!
                    if hasattr(pipe_i2v, "enable_attention_slicing"):
                        pipe_i2v.enable_attention_slicing()
                    
                    if "," in image_base64:
                        image_base64 = image_base64.split(",")[1]
                    image_bytes = base64.b64decode(image_base64)
                    
                    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    kwargs["image"] = image
                    
                    out = pipe_i2v(**kwargs)
                else:
                    print("[LTXEngine] Gerando vídeo a partir de TEXTO (T2V)...")
                    if hasattr(self.pipe_t2v, "enable_attention_slicing"):
                        self.pipe_t2v.enable_attention_slicing()
                    out = self.pipe_t2v(**kwargs)
            
            video = out.frames[0]
            
            out_path = "/tmp/ltx_out.mp4"
            
            if hasattr(out, "audio") and out.audio is not None:
                print("[LTXEngine] Áudio nativo detectado! Muxando áudio no MP4...")
                from diffusers.utils import export_utils
                audio_tensor = out.audio[0] if out.audio.ndim == 3 else out.audio
                export_utils.encode_video(video, out_path, fps=frame_rate, audio=audio_tensor, audio_sample_rate=48000)
            else:
                print("[LTXEngine] Nenhum áudio nativo. Exportando vídeo mudo...")
                export_to_video(video, out_path, fps=frame_rate)

            with open(out_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")

            # Memory cleanup
            del video
            torch.cuda.empty_cache()

            render_time = time.time() - t0
            return {
                "status": "success",
                "video_base64": b64,
                "render_time_seconds": round(render_time, 2),
                "resolution": f"{w}x{h}",
                "engine": "LTX-13B (v2.3) I2V" if image_base64 else "LTX-13B (v2.3) T2V",
                "estimated_cost_usd": round(render_time * 0.00114, 4) 
            }

        except Exception as e:
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
