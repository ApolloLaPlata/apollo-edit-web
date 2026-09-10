import modal
import os

app = modal.App("test-audiosr")

def download_audiosr():
    import torch
    from audiosr import build_model
    # Isso vai forçar o download dos pesos básicos do AudioSR para o cache
    build_model(model_name="basic", device="cpu")

audiosr_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install("torch", "torchaudio", "soundfile", "numpy", "transformers", "huggingface_hub", "setuptools<70.0.0", "matplotlib<3.8.0", "torchcodec")
    .run_commands("pip install git+https://github.com/haoheliu/versatile_audio_super_resolution.git")
    .run_function(download_audiosr)
)

@app.function(image=audiosr_image, gpu="A10G", timeout=600)
def run_audiosr(audio_bytes: bytes):
    import tempfile
    import os
    import soundfile as sf
    from audiosr import build_model, super_resolution
    
    with tempfile.TemporaryDirectory() as tmpdir:
        in_path = os.path.join(tmpdir, "in.wav")
        with open(in_path, "wb") as f:
            f.write(audio_bytes)
            
        print("[AudioSR] Carregando modelo 'basic'...")
        audiosr_model = build_model(model_name="basic", device="cuda")
        
        print("[AudioSR] Rodando Super Resolução no áudio...")
        waveform = super_resolution(
            audiosr_model,
            in_path,
            seed=42,
            guidance_scale=3.0, # (era 3.5) Reduzido para preservar attack de graves e não metalizar
            ddim_steps=40       # (era 50) Sweet spot pra evitar "ringing" em HF
        )
        
        import io
        import numpy as np
        
        if isinstance(waveform, list):
            waveform = waveform[0]
            
        audio_array = waveform.squeeze()
        # Se tiver mais de uma dimensão depois do squeeze, transpõe para o soundfile
        if audio_array.ndim == 2:
            audio_array = audio_array.T
            
        out_io = io.BytesIO()
        sf.write(out_io, audio_array, 48000, format='WAV')
        return out_io.getvalue()

@app.local_entrypoint()
def main():
    print("Iniciando laboratório AudioSR (Upscaler 16kHz -> 48kHz)...")
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    in_file = "LABORATORIO_MODAIS/testes_audio/ace_step_test.wav"
    if not os.path.exists(in_file):
        print(f"Erro: {in_file} não encontrado!")
        return
        
    print(f"Lendo {in_file}...")
    with open(in_file, "rb") as f:
        in_bytes = f.read()
        
    print("Enviando para Nuvem (A10G)...")
    out_bytes = run_audiosr.remote(in_bytes)
    
    out_file = "LABORATORIO_MODAIS/testes_audio/4_ace_step_audiosr_test.wav"
    with open(out_file, "wb") as f:
        f.write(out_bytes)
        
    print(f"✅ Salvo AudioSR em {out_file}")
