import modal
import os
import time

app = modal.App("stable-audio-3-pingpong")
volume = modal.Volume.from_name("apollo-models", create_if_missing=True)

image = modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10") \
    .apt_install("git", "ffmpeg") \
    .pip_install("torch", "torchaudio", "torchvision", extra_options="--index-url https://download.pytorch.org/whl/cu121") \
    .pip_install("numpy<2", "einops", "safetensors", "soundfile", "huggingface_hub", "pytorch_lightning") \
    .run_commands("git clone https://github.com/Stability-AI/stable-audio-tools.git /stable-audio-tools") \
    .run_commands("cd /stable-audio-tools && pip install -e .")

@app.cls(gpu="H100", image=image, timeout=3600, memory=32768, volumes={"/models": volume})
class StableAudio3EnginePingPong:
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
    def generate(self, prompt: str, seconds: int = 120):
        import torch
        from stable_audio_tools.inference.generation import generate_diffusion_cond_inpaint
        import torchaudio
        from einops import rearrange
        import io
        import time

        steps = 8
        cfg = 1.0
        
        print(f"Gerando {seconds}s no Stable Audio 3 Medium para: {prompt} (CFG: {cfg}, Steps: {steps}, Sampler: PINGPONG)")
        start = time.time()
        
        conditioning = [{"prompt": prompt, "seconds_start": 0, "seconds_total": seconds}]
        
        with torch.no_grad():
            output = generate_diffusion_cond_inpaint(
                self.model,
                steps=steps,
                cfg_scale=cfg,
                conditioning=conditioning,
                sample_size=self.sample_size, 
                sampler_type="pingpong", # O SAMPLER SECRETO DO MODELO DISTILADO
                device="cuda"
            )
            
        output = rearrange(output, "b d n -> d (b n)")
        output = output.to(torch.float32)
        output = output.div(torch.max(torch.abs(output))).clamp(-1, 1).mul(32767).to(torch.int16).cpu()
        
        print(f"Gerado em {time.time()-start:.1f} segundos!")
        
        buffer = io.BytesIO()
        torchaudio.save(buffer, output, self.sample_rate, format="wav")
        
        import base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

@app.local_entrypoint()
def run_tests():
    import base64
    os.makedirs("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_sa3_pingpong", exist_ok=True)
    engine = StableAudio3EnginePingPong()
    
    tasks = [
        {
            "name": "Instrumental_Cinematico_PingPong",
            "prompt": "epic cinematic orchestral score, hans zimmer style, massive brass, soaring strings, thunderous percussion, highly emotional, 4k audio, high quality",
            "duration": 120
        },
        {
            "name": "Instrumental_Trap_PingPong",
            "prompt": "hard dark trap beat, instrumental no vocals, heavy distorted 808 bass, fast hi-hats, spooky synth melody, 140 bpm, crisp mix, high quality",
            "duration": 120
        }
    ]
    
    print(f"Enviando bateria de testes PING-PONG (Distilled Original) para o modelo *Stable Audio 3 Medium*...")
    
    for task in tasks:
        print(f"Gerando {task['name']}...")
        wav_base64 = engine.generate.remote(prompt=task["prompt"], seconds=task["duration"])
        wav_data = base64.b64decode(wav_base64)
        
        timestamp = int(time.time())
        out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_sa3_pingpong/{task['name']}_{timestamp}.wav"
        
        with open(out_path, "wb") as f:
            f.write(wav_data)
        
        print(f"[SUCESSO] Salvo em: {out_path}")

