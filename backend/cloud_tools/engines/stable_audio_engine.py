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
        
        login("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")
        
        print("Baixando configs e pesos do Stable Audio 3 Medium...")
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
        print("Stable Audio 3 Medium carregado com sucesso!")

    @modal.method()
    def generate_audio(self, prompt: str, duration_s: float = 120, steps: int = 100, cfg: float = 7.0):
        import torch
        # FIX: USAR A FUNCAO CORRETA DE GERACAO PURA, NAO A DE INPAINT
        from stable_audio_tools.inference.generation import generate_diffusion_cond
        import torchaudio
        from einops import rearrange
        import io
        import time

        print(f"Gerando {duration_s}s no Stable Audio 3 Medium para: {prompt} (CFG: {cfg}, Steps: {steps})")
        start = time.time()
        
        conditioning = [{"prompt": prompt, "seconds_start": 0, "seconds_total": int(duration_s)}]
        
        with torch.no_grad():
            output = generate_diffusion_cond(
                self.model,
                steps=steps,
                cfg_scale=cfg,
                conditioning=conditioning,
                sample_size=self.sample_size, 
                sigma_min=0.3, # PARAMETRO OBRIGATORIO FALTANTE
                sigma_max=500, # PARAMETRO OBRIGATORIO FALTANTE
                sampler_type="dpmpp-3m-sde", # SAMPLER OBRIGATORIO OFICIAL
                device="cuda"
            )
            
        # FIX: Rearranjo correto dos tensores baseados na documentacao oficial
        output = rearrange(output, "b d n -> d (b n)")
        
        # FIX: Normalizacao nativa usando Torch
        output = output.to(torch.float32).div(torch.max(torch.abs(output))).clamp(-1, 1)
        
        print(f"Gerado em {time.time()-start:.1f} segundos!")
        
        buffer = io.BytesIO()
        torchaudio.save(buffer, output.cpu(), self.sample_rate, format="wav")
        
        import base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

