import os
import modal
import base64

bark_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "build-essential")
    .run_commands("git clone https://github.com/serp-ai/bark-with-voice-clone.git /bark")
    .run_commands("pip install \"pip<24.1\"")
    .pip_install("torch", "torchaudio", "torchvision", "numpy", "scipy", "transformers", "huggingface_hub", "encodec", "audiolm-pytorch", "torchcodec", "soundfile")
    .run_commands("pip install git+https://github.com/pytorch/fairseq.git")
    .run_commands("cd /bark && pip install -r requirements.txt || true")
    .run_commands("pip install git+https://github.com/suno-ai/bark.git")
)

app = modal.App("apollo-bark-test")

@app.function(image=bark_image, gpu="L4", timeout=1200)
def generate_bark(text: str, ref_wav_bytes: bytes):
    import sys
    sys.path.append("/bark")
    import os
    import numpy as np
    import torch
    import functools
    
    # [MONKEYPATCH] PyTorch 2.6+ setou weights_only=True por padrão e quebrou bibliotecas antigas. 
    # Forçamos False globalmente para o HuBERT carregar os pesos em paz.
    _original_load = torch.load
    torch.load = functools.partial(_original_load, weights_only=False)
    
    import torchaudio
    
    with open("/tmp/audio.wav", "wb") as f:
        f.write(ref_wav_bytes)
        
    print("Loading models...")
    from bark.generation import load_codec_model, generate_text_semantic, SAMPLE_RATE, preload_models, codec_decode, generate_coarse, generate_fine
    from encodec.utils import convert_audio
    
    device = 'cuda'
    model = load_codec_model(use_gpu=True)
    
    from hubert.hubert_manager import HuBERTManager
    hubert_manager = HuBERTManager()
    hubert_manager.make_sure_hubert_installed()
    hubert_manager.make_sure_tokenizer_installed()
    
    from hubert.pre_kmeans_hubert import CustomHubert
    from hubert.customtokenizer import CustomTokenizer
    
    hubert_model = CustomHubert(checkpoint_path='data/models/hubert/hubert.pt').to(device)
    tokenizer = CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth').to(device)
    
    print("Processing audio...")
    wav, sr = torchaudio.load("/tmp/audio.wav")
    wav = convert_audio(wav, sr, model.sample_rate, model.channels)
    wav = wav.to(device)
    
    semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
    semantic_tokens = tokenizer.get_token(semantic_vectors)
    
    with torch.no_grad():
        encoded_frames = model.encode(wav.unsqueeze(0))
    codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()
    
    codes = codes.cpu().numpy()
    semantic_tokens = semantic_tokens.cpu().numpy()
    
    npz_path = "/tmp/my_voice.npz"
    np.savez(npz_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)
    
    print("Preloading Bark models...")
    preload_models(
        text_use_gpu=True, text_use_small=False,
        coarse_use_gpu=True, coarse_use_small=False,
        fine_use_gpu=True, fine_use_small=False,
        codec_use_gpu=True, force_reload=False
    )
    
    print(f"Generating audio for: {text}")
    x_semantic = generate_text_semantic(
        text,
        history_prompt=npz_path,
        temp=0.7,
        top_k=50,
        top_p=0.95,
    )
    x_coarse_gen = generate_coarse(
        x_semantic,
        history_prompt=npz_path,
        temp=0.7,
        top_k=50,
        top_p=0.95,
    )
    x_fine_gen = generate_fine(
        x_coarse_gen,
        history_prompt=npz_path,
        temp=0.5,
    )
    audio_array = codec_decode(x_fine_gen)
    
    import io
    from scipy.io.wavfile import write as write_wav
    out_io = io.BytesIO()
    write_wav(out_io, SAMPLE_RATE, audio_array)
    return out_io.getvalue()

@app.local_entrypoint()
def main():
    print("\n--- INICIANDO TESTE: BARK (Zero-Shot Clone via HuBERT) ---")
    
    ref_audio = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    with open(ref_audio, "rb") as f:
        audio_data = f.read()
        
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\bark"
    os.makedirs(save_dir, exist_ok=True)
    
    tests = {
        "pt_test": "Olá, Mestre! Eu estou testando se essa voz consegue falar em português do Brasil, ou se eu vou bugar o sistema inteiro.",
        "laugh_start": "[laughs] Oh my god, this is absolutely hilarious!",
        "cry_start": "[sighs] I just... I can't take this anymore. It hurts."
    }
    
    for name, text in tests.items():
        print(f"\n[Bark] Generating: {name} -> {text}")
        try:
            wav_bytes = generate_bark.remote(text, audio_data)
            save_path = os.path.join(save_dir, f"{name}.wav")
            with open(save_path, "wb") as f:
                f.write(wav_bytes)
            print(f"-> Salvo: {save_path}")
        except Exception as e:
            print(f"Erro em {name}: {e}")
            
    print("\n--- TESTE BARK CONCLUÍDO ---")
