import modal
import os

app = modal.App("test-musicgen")

def download_musicgen():
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    AutoProcessor.from_pretrained("facebook/musicgen-small")
    MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")

musicgen_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("torch", "transformers", "accelerate", "soundfile", "torchaudio")
    .run_function(download_musicgen)
)

@app.function(image=musicgen_image, gpu="A10G")
def run_musicgen():
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import soundfile as sf
    import io
    
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to("cuda")
    
    prompt = "Cinematic epic orchestral trailer music with heavy drums and brass"
    print(f"Gerando MusicGen com prompt: {prompt}")
    
    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to("cuda")
    # max_new_tokens=500 -> aprox 10 segundos no MusicGen
    audio_values = model.generate(**inputs, max_new_tokens=500)
    
    import numpy as np
    audio = audio_values[0, 0].cpu().numpy().astype(np.float32)
    
    out_io = io.BytesIO()
    sf.write(out_io, audio, model.config.audio_encoder.sampling_rate, format='WAV')
    return out_io.getvalue()

@app.local_entrypoint()
def main():
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    print("Iniciando bateria MusicGen (O Clássico da Meta, 32kHz)...")
    audio_bytes = run_musicgen.remote()
    with open("LABORATORIO_MODAIS/testes_audio/3_musicgen_test.wav", "wb") as f:
        f.write(audio_bytes)
    print("✅ Salvo MusicGen em LABORATORIO_MODAIS/testes_audio/3_musicgen_test.wav!")
