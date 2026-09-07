"""
Motor de Geracao de Audio e Musica - Stable Audio 3 Medium (PingPong Sampler)
====================================================================
Substituido do diffusers pipeline para usar o stable-audio-tools original
com o sampler 'pingpong' (ideal para o modelo destilado Medium).
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import time

volume = modal.Volume.from_name("apollo-models", create_if_missing=True)

stable_audio_image = (
    modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10")
    .apt_install("git", "ffmpeg")
    .pip_install("torch", "torchaudio", "torchvision", extra_options="--index-url https://download.pytorch.org/whl/cu121")
    .pip_install("numpy<2", "einops", "safetensors", "soundfile", "huggingface_hub", "pytorch_lightning", "fastapi[standard]")
    .run_commands("git clone https://github.com/Stability-AI/stable-audio-tools.git /stable-audio-tools")
    .run_commands("cd /stable-audio-tools && pip install -e .")
)

@app.cls(gpu="A10G", image=stable_audio_image, timeout=600, scaledown_window=30, min_containers=0, volumes={"/models": volume}, secrets=[modal.Secret.from_name("huggingface-secret")])
class StableAudioEngine:
    @modal.enter()
    def setup(self):
        import torch
        from stable_audio_tools.models.factory import create_model_from_config
        from stable_audio_tools.models.utils import load_ckpt_state_dict
        from huggingface_hub import login, hf_hub_download
        import json
        
        token = os.environ.get("HF_TOKEN")
        if token:
            login(token)
            
        print("[INIT] Baixando configs e pesos do Stable Audio 3 Medium (PingPong)...")
        config_path = hf_hub_download(repo_id="stabilityai/stable-audio-3-medium", filename="model_config.json", cache_dir="/models/huggingface_cache")
        ckpt_path = hf_hub_download(repo_id="stabilityai/stable-audio-3-medium", filename="model.safetensors", cache_dir="/models/huggingface_cache")
        
        with open(config_path) as f:
            model_config = json.load(f)

        self.model = create_model_from_config(model_config)
        self.model.load_state_dict(load_ckpt_state_dict(ckpt_path))
        
        self.sample_rate = model_config["sample_rate"]
        self.sample_size = model_config["sample_size"]
        
        self.model.to("cuda")
        self.model.eval()
        print("[INIT] Stable Audio 3 Medium carregado com sucesso!")

    @modal.method()
    def generate_audio(self, prompt: str, duration_s: float = 120.0, num_inference_steps: int = 8, seed: int = 0):
        import torch
        from stable_audio_tools.inference.generation import generate_diffusion_cond_inpaint
        import torchaudio
        from einops import rearrange
        import io
        import time

        steps = 8 # HARDCODED para destilado
        cfg = 1.0 # HARDCODED para destilado
        duration_s = int(duration_s)
        
        print(f"[GEN] Gerando {duration_s}s no SA3 Medium | Prompt: {prompt[:50]}... | CFG: {cfg}, Steps: {steps}, Sampler: pingpong")
        start = time.time()
        
        master_prompt = prompt + ", high quality, 4k audio, high fidelity, clean, sharp, stereo, masterpiece"
        conditioning = [{"prompt": master_prompt, "seconds_start": 0, "seconds_total": duration_s}]
        
        with torch.no_grad():
            output = generate_diffusion_cond_inpaint(
                self.model,
                steps=steps,
                cfg_scale=cfg,
                conditioning=conditioning,
                sample_size=self.sample_size, 
                sampler_type="pingpong",
                device="cuda"
            )
            
        output = rearrange(output, "b d n -> d (b n)")
        output = output.to(torch.float32)
        output = output.div(torch.max(torch.abs(output))).clamp(-1, 1).mul(32767).to(torch.int16).cpu()
        
        print(f"[GEN] Concluido em {time.time()-start:.1f} segundos!")
        
        buffer = io.BytesIO()
        torchaudio.save(buffer, output, self.sample_rate, format="wav")
        
        return buffer.getvalue()

    @modal.fastapi_endpoint(method="POST", label="apollo-api-stable-audio")
    async def api_stable_audio(self, request: dict):
        from fastapi.responses import Response, JSONResponse
        try:
            data = request
            prompt = data.get("prompt", "")
            duration_s = data.get("duration_s", 30.0)
            if not prompt: return JSONResponse({"error": "No prompt provided"}, status_code=400)
            wav_bytes = self.generate_audio.local(prompt, duration_s, 8, 0)
            return Response(content=wav_bytes, media_type="audio/wav")
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
