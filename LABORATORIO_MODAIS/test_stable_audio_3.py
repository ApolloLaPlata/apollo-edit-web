import modal
import os
import time

app = modal.App("stable-audio-3-engine")

image = modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10") \
    .apt_install("git", "ffmpeg") \
    .pip_install("torch", "torchaudio", "torchvision", extra_options="--index-url https://download.pytorch.org/whl/cu121") \
    .pip_install("numpy<2", "einops", "safetensors", "soundfile", "huggingface_hub", "pytorch_lightning") \
    .run_commands("git clone https://github.com/Stability-AI/stable-audio-tools.git /stable-audio-tools") \
    .run_commands("cd /stable-audio-tools && pip install -e .")

@app.cls(gpu="H100", image=image, timeout=3600, memory=32768)
class StableAudio3Engine:
    @modal.enter()
    def setup(self):
        import torch
        from stable_audio_tools.models.factory import create_model_from_config
        from stable_audio_tools.models.utils import load_ckpt_state_dict
        from huggingface_hub import login, hf_hub_download
        import json
        
        login("hf_XXX_REMOVED_SECRET")
        
        print("Baixando configs e pesos do Stable Audio 3 Medium...")
        config_path = hf_hub_download(repo_id="stabilityai/stable-audio-3-medium", filename="model_config.json")
        ckpt_path = hf_hub_download(repo_id="stabilityai/stable-audio-3-medium", filename="model.safetensors")
        
        with open(config_path) as f:
            model_config = json.load(f)

        self.model = create_model_from_config(model_config)
        self.model.load_state_dict(load_ckpt_state_dict(ckpt_path))
        
        self.sample_rate = model_config["sample_rate"]
        self.sample_size = model_config["sample_size"]
        
        self.model.to("cuda")
        self.model.eval()
        print("Stable Audio 3 carregado com sucesso!")

    @modal.method()
    def generate(self, prompt: str, seconds: int = 47):
        import torch
        from stable_audio_tools.inference.generation import generate_diffusion_cond_inpaint
        import soundfile as sf
        import io
        import time
        from huggingface_hub import login
        
        login("hf_XXX_REMOVED_SECRET")

        print(f"Gerando {seconds}s no Stable Audio 3 para: {prompt}")
        start = time.time()
        
        conditioning = [{"prompt": prompt, "seconds_start": 0, "seconds_total": seconds}]
        
        with torch.no_grad():
            output = generate_diffusion_cond_inpaint(
                self.model,
                steps=250,
                cfg_scale=7.0,
                conditioning=conditioning,
                sample_size=self.sample_size,
                sampler_type="dpmpp",
                device="cuda"
            )
            
        output = output.cpu().numpy().squeeze(0)
        
        print(f"Gerado em {time.time()-start:.1f} segundos!")
        
        buffer = io.BytesIO()
        sf.write(buffer, output.T, self.sample_rate, format='WAV')
        return buffer.getvalue()

@app.local_entrypoint()
def run_test():
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    engine = StableAudio3Engine()
    prompt = "128 BPM, Deep House, Four on the floor kick, Groovy Bassline, Synth chords, Instrumental"
    print("Iniciando requisicao para Stable Audio 3 Medium...")
    wav_data = engine.generate.remote(prompt, 47)
    
    timestamp = int(time.time())
    out_path = f"LABORATORIO_MODAIS/testes_audio/StableAudio3_Inst_{timestamp}.wav"
    with open(out_path, "wb") as f:
        f.write(wav_data)
    print(f"Salvo em: {out_path}")

