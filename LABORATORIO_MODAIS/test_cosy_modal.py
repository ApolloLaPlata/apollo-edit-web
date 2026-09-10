import modal

def download_models():
    from modelscope import snapshot_download
    print("Baixando os pesos do CosyVoice2-0.5B na etapa de build...")
    snapshot_download('iic/CosyVoice2-0.5B')

cosy_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "sox", "libsox-dev", "build-essential")
    .run_commands(
        "git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git /workspace/CosyVoice",
        "cd /workspace/CosyVoice && sed -i '/openai-whisper/d' requirements.txt && sed -i '/deepspeed/d' requirements.txt && pip install -r requirements.txt",
        "pip install --no-build-isolation openai-whisper==20231117",
        "pip install modelscope pydantic fastapi ormsgpack"
    )
    .env({"PYTHONPATH": "/workspace/CosyVoice/third_party/Matcha-TTS:/workspace/CosyVoice", "MODELSCOPE_CACHE": "/models/modelscope_cache"})
)

app = modal.App("test-cosyvoice2", image=cosy_image)
vol = modal.Volume.from_name("apollo-voice-models", create_if_missing=True)

@app.function(gpu="L4", timeout=600, volumes={"/models": vol})
def test_load():
    import sys
    sys.path.insert(0, "/workspace/CosyVoice/third_party/Matcha-TTS")
    sys.path.insert(0, "/workspace/CosyVoice")
    from cosyvoice.cli.cosyvoice import CosyVoice2
    from modelscope import snapshot_download
    
    print("Recuperando cache do CosyVoice2-0.5B...")
    model_dir = snapshot_download('iic/CosyVoice2-0.5B', cache_dir='/models/modelscope_cache')
    print(f"Model directory: {model_dir}")
    
    print("Loading CosyVoice2...")
    cosyvoice = CosyVoice2(model_dir, load_jit=False, load_trt=False, fp16=True)
    print("Success! CosyVoice2 is loaded and ready.")
    return True

@app.local_entrypoint()
def main():
    print("Iniciando teste de build do CosyVoice2-0.5B na Modal (Com Bake-in Snapshot)...")
    test_load.remote()
    print("Teste concluído com sucesso.")
