import modal
import os

app = modal.App("test-stable-audio")

stable_audio_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("torch", "transformers", "diffusers", "accelerate", "soundfile", "torchaudio", "torchsde")
)

@app.function(image=stable_audio_image, gpu="A10G", secrets=[modal.Secret.from_name("my-huggingface-secret")], timeout=1200)
def run_stable_audio():
    import torch
    import soundfile as sf
    import io
    from diffusers import StableAudioPipeline
    
    print("Carregando Stable Audio Open 1.0 na VRAM...")
    pipe = StableAudioPipeline.from_pretrained("stabilityai/stable-audio-open-1.0", torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    
    # Prompt com práticas para SFX orgânico
    prompt = "footsteps on wet grass, single person, medium pace, recorded close-up, no music, organic foley"
    negative_prompt = "synthesized, electronic, tonal, glitch, low quality, noisy"
    
    print(f"Gerando áudio com prompt: {prompt}")
    
    # Valores de Sweet Spot para SFX orgânico!
    audio = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=70, 
        guidance_scale=4.0,
        audio_end_in_s=8.0
    ).audios[0]
    
    import numpy as np
    if hasattr(audio, "cpu"):
        audio = audio.cpu().numpy()
    audio = audio.astype(np.float32)
    out_io = io.BytesIO()
    # Stable audio gera a 44.1kHz por padrão
    sf.write(out_io, audio.T if audio.ndim == 2 else audio, 44100, format='WAV')
    return out_io.getvalue()

@app.local_entrypoint()
def main():
    print("Iniciando bateria Stable Audio Open 1.0 (Foley/SFX Limpo)...")
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    audio_bytes = run_stable_audio.remote()
    out_path = "LABORATORIO_MODAIS/testes_audio/stable_audio_test.wav"
    
    with open(out_path, "wb") as f:
        f.write(audio_bytes)
        
    print(f"✅ Salvo Stable Audio Open em {out_path}!")
