"""
Apollo Modal Engine — Wan2.1 (Tier 1 / Tier 2)
==============================================
Suporta Text-to-Video (T2V) e Image-to-Video (I2V).
- T2V usa o modelo 1.3B (gpu="A100" ou "L4")
- I2V usa o modelo 14B-480P (gpu="A100" mandatório)
"""

import base64
import os
import traceback
import io
from pathlib import Path
import modal

from backend.cloud_tools.modal_app import app

MODEL_T2V_DIR = "/models/wan21_1_3b"
MODEL_I2V_DIR = "/models/wan21_i2v_14b"

# Imagem Docker para o Wan2.1
wan_image = (
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
        "Pillow"
    )
    .env({
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
        "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
    })
    .run_commands(
        [
            "python -c \"from huggingface_hub import snapshot_download; "
            "from pathlib import Path; "
            "print('[BUILD] Downloading Wan-AI/Wan2.1-T2V-1.3B-Diffusers...'); "
            "snapshot_download(repo_id='Wan-AI/Wan2.1-T2V-1.3B-Diffusers', local_dir='/models/wan21_1_3b', local_dir_use_symlinks=False); "
            "print('[BUILD] Downloading Wan-AI/Wan2.1-I2V-14B-480P-Diffusers...'); "
            "snapshot_download(repo_id='Wan-AI/Wan2.1-I2V-14B-480P-Diffusers', local_dir='/models/wan21_i2v_14b', local_dir_use_symlinks=False); \""
        ]
    )
    .env({
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
    })
)

PRESETS = {
    "standard": {
        "num_inference_steps": 50,
        "width": 832,
        "height": 480,
        "guidance_scale": 5.0
    },
    "fast": {
        "num_inference_steps": 25,
        "width": 832,
        "height": 480,
        "guidance_scale": 5.0
    },
    "pro": {
        "num_inference_steps": 40,
        "width": 1280,
        "height": 720,
        "guidance_scale": 5.0
    }
}

# Mudamos para A100 porque o modelo 14B de I2V não cabe na L4
@app.cls(gpu="a10g", timeout=1200, image=wan_image, enable_memory_snapshot=True, experimental_options={"enable_gpu_snapshot": True})
class Wan21Engine:
    @modal.enter(snap=True)
    def load_model(self):
        import torch
        from diffusers import WanPipeline, WanImageToVideoPipeline, WanTransformer3DModel
        from transformers import BitsAndBytesConfig, AutoModel

        torch.set_grad_enabled(False)
        print("[WanEngine] Carregando text_encoder (UMT5) em 8-bit...")
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        
        text_encoder = AutoModel.from_pretrained(
            MODEL_T2V_DIR,
            subfolder="text_encoder",
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )

        print("[WanEngine] Carregando Wan2.1-T2V-1.3B transformer em 8-bit...")
        transformer_t2v = WanTransformer3DModel.from_pretrained(
            MODEL_T2V_DIR,
            subfolder="transformer",
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )
        self.pipe_t2v = WanPipeline.from_pretrained(
            MODEL_T2V_DIR,
            text_encoder=text_encoder,
            transformer=transformer_t2v,
            torch_dtype=torch.bfloat16,
            local_files_only=True,
        ).to("cuda")

        print("[WanEngine] Carregando Wan2.1-I2V-14B-480P transformer em 8-bit...")
        transformer_i2v = WanTransformer3DModel.from_pretrained(
            MODEL_I2V_DIR,
            subfolder="transformer",
            quantization_config=quantization_config,
            torch_dtype=torch.bfloat16,
            local_files_only=True
        )
        self.pipe_i2v = WanImageToVideoPipeline.from_pretrained(
            MODEL_I2V_DIR,
            text_encoder=text_encoder,
            transformer=transformer_i2v,
            torch_dtype=torch.bfloat16,
            local_files_only=True,
        ).to("cuda")

    @modal.method()
    def generate(self, prompt: str, image_base64: str = None, duration: int = 5, preset: str = "fast", aspect_ratio: str = "horizontal", seed: int = 42) -> dict:
        import time
        import torch
        from diffusers.utils import export_to_video
        from PIL import Image

        t0 = time.time()
        print(f"[WanEngine] Request: {prompt[:50]}... | Preset: {preset} | Dur: {duration}s | I2V: {bool(image_base64)} | Formato: {aspect_ratio}")
        
        cfg = PRESETS.get(preset, PRESETS["fast"])
        
        # Ajusta dimensões baseado no formato (Mantém a resolução total aproximada do preset)
        w, h = cfg["width"], cfg["height"]
        if aspect_ratio == "vertical":
            # Inverte as dimensões
            w, h = cfg["height"], cfg["width"]
        elif aspect_ratio == "square":
            # Pega a média para formar o quadrado (multiplos de 16)
            avg = int(((w + h) / 2) // 16 * 16)
            w, h = avg, avg
            
        num_frames = (duration * 16) + 1
        generator = torch.Generator(device="cpu").manual_seed(seed)

        try:
            torch.cuda.empty_cache()
            
            if image_base64:
                # Image to Video
                print("[WanEngine] Iniciando Image-to-Video (14B)")
                # decodificar imagem
                if "," in image_base64:
                    image_base64 = image_base64.split(",")[1]
                image_bytes = base64.b64decode(image_base64)
                init_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                
                output = self.pipe_i2v(
                    prompt=prompt,
                    image=init_image,
                    negative_prompt="low quality, bad anatomy, worst quality, distorted, blurry",
                    height=h,
                    width=w,
                    num_frames=num_frames,
                    guidance_scale=cfg["guidance_scale"],
                    num_inference_steps=cfg["num_inference_steps"],
                    generator=generator,
                    output_type="pil"
                )
            else:
                # Text to Video
                print("[WanEngine] Iniciando Text-to-Video (1.3B)")
                output = self.pipe_t2v(
                    prompt=prompt,
                    negative_prompt="low quality, bad anatomy, worst quality, distorted, blurry",
                    height=h,
                    width=w,
                    num_frames=num_frames,
                    guidance_scale=cfg["guidance_scale"],
                    num_inference_steps=cfg["num_inference_steps"],
                    generator=generator,
                    output_type="pil"
                )
            
            vid_tensor = output.frames[0]
            out_path = "/tmp/wan_out.mp4"
            export_to_video(vid_tensor, out_path, fps=16)

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
                "engine": "Wan2.1-I2V-14B" if image_base64 else "Wan2.1-T2V-1.3B",
                "estimated_cost_usd": round(render_time * 0.00114, 4) # A100 cost
            }

        except Exception as e:
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
