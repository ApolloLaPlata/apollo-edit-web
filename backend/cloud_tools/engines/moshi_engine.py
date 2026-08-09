import modal
import os

# A imagem do Moshi precisa de rustc/cargo instalados para compilar alguns pacotes
moshi_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "curl", "build-essential")
    .run_commands("curl https://sh.rustup.rs -sSf | sh -s -- -y")
    .env({"PATH": "/root/.cargo/bin:$PATH"})
    .pip_install(
        "torch>=2.3.0",
        "torchaudio>=2.3.0",
        "huggingface_hub",
        "numpy",
        "sentencepiece",
        "safetensors"
    )
    .run_commands(
        "pip install moshi",
        "huggingface-cli download kyutai/moshiko-pytorch-bf16"
    )
)

app = modal.App("apollo-moshi-engine")

# Usamos modal.web_server para expor a porta em que o servidor interno do Moshi roda.
@app.function(
    image=moshi_image,
    gpu="L4",
    timeout=1800, # 30 minutos de limite de ligação
    scaledown_window=30,
    min_containers=0
)
@modal.web_server(port=8000, label="apollo-api-moshi")
def moshi_server():
    import subprocess
    import os
    
    print("[INIT] Iniciando Servidor Moshi com Gradio Tunnel...")
    # Usando o gradio-tunnel para termos a UI de testes pronta instantaneamente
    subprocess.Popen(
        ["python", "-m", "moshi.server", "--host", "0.0.0.0", "--port", "8000", "--hf-repo", "kyutai/moshiko-pytorch-bf16", "--gradio-tunnel"],
        env=os.environ.copy()
    ).wait()
