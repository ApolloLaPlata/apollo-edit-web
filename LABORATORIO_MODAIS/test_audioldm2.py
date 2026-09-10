import modal
import os

app = modal.App("test-audioldm2")

def download_audioldm2():
    import torch
    from diffusers import AudioLDM2Pipeline
    AudioLDM2Pipeline.from_pretrained("cvssp/audioldm2", torch_dtype=torch.float16)

audioldm2_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("torch", "transformers==4.38.2", "diffusers==0.27.2", "accelerate", "soundfile", "torchaudio")
    .run_function(download_audioldm2)
)

@app.function(image=audioldm2_image, gpu="A10G")
def run_audioldm2():
    import torch
    from diffusers import AudioLDM2Pipeline
    import soundfile as sf
    import io
    
    pipe = AudioLDM2Pipeline.from_pretrained("cvssp/audioldm2", torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    
    prompt = "Cinematic epic orchestral trailer music with heavy drums and brass"
    print(f"Gerando AudioLDM2 com prompt: {prompt}")
    
    audio = pipe(prompt, num_inference_steps=100, audio_length_in_s=10.0).audios[0]
    
    import numpy as np
    audio = audio.astype(np.float32)
    out_io = io.BytesIO()
    sf.write(out_io, audio.T if audio.ndim == 2 else audio, 16000, format='WAV')
    return out_io.getvalue()

@app.local_entrypoint()
def main():
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    print("Iniciando bateria AudioLDM2 (O 'Menorzinho' de 16kHz)...")
    audio_bytes = run_audioldm2.remote()
    with open("LABORATORIO_MODAIS/testes_audio/2_audioldm2_test.wav", "wb") as f:
        f.write(audio_bytes)
    print("✅ Salvo AudioLDM2 em LABORATORIO_MODAIS/testes_audio/2_audioldm2_test.wav!")
