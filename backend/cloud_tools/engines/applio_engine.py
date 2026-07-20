import os
import subprocess
import modal

app = modal.App("apollo-applio-web")
vol = modal.Volume.from_name("apollo-applio-data", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "wget", "curl", "libgl1-mesa-glx", "libglib2.0-0")
    .run_commands("git clone https://github.com/IAHispano/Applio /applio")
    .workdir("/applio")
    # Instalamos as dependencias vitais de ML base do RVC
    .pip_install(
        "numpy==1.26.4",
        "requests>=2.31.0,<2.32.0",
        "tqdm",
        "wget",
        "ffmpeg-python>=0.2.0",
        "faiss-cpu==1.7.3",
        "librosa==0.11.0",
        "scipy==1.11.1",
        "soundfile==0.12.1",
        "noisereduce",
        "pedalboard",
        "stftpitchshift",
        "soxr",
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "torchvision",
        "torchcrepe==0.0.23",
        "torchfcpe",
        "swift_f0",
        "einops",
        "transformers==4.44.2",
        "matplotlib==3.7.2",
        "tensorboard",
        "gradio==5.23.1",
        "tensorboardX",
        "tensorflow",
        "edge-tts==7.2.0",
        "pypresence",
        "beautifulsoup4",
        "sounddevice",
        "webrtcvad",
        "omegaconf>=2.0.6",
        "certifi>=2023.07.22"
    )
    .run_commands("mkdir -p /applio/data")
)

@app.function(
    image=image,
    gpu="L4",  # L4 or A10G is great for training RVC
    volumes={"/applio/data": vol},
    timeout=86400  # 24 hours para permitir treinamentos longos
)
@modal.web_server(port=8000)
def run_applio():
    import os
    import subprocess
    import shutil
    
    # Ensure directories exist in the persistent volume
    os.makedirs("/applio/data/logs", exist_ok=True)
    os.makedirs("/applio/data/weights", exist_ok=True)
    os.makedirs("/applio/data/datasets", exist_ok=True)
    os.makedirs("/applio/data/audios", exist_ok=True)
    
    # Em conteineres imutaveis, se a pasta ja existe, nos a deletamos e linkamos para o volume
    for folder in ["logs", "assets/weights", "assets/datasets", "assets/audios"]:
        target = f"/applio/{folder}"
        source = f"/applio/data/{os.path.basename(folder)}"
        if os.path.exists(target) and not os.path.islink(target):
            shutil.rmtree(target, ignore_errors=True)
        if not os.path.exists(target):
            os.symlink(source, target)
            
    print("Roteamento de Volume Persistente Applio Concluido!")
    
    # Run Applio Gradio UI natively bound to 0.0.0.0 on port 8000
    env = os.environ.copy()
    env["GRADIO_SERVER_PORT"] = "8000"
    env["GRADIO_SERVER_NAME"] = "0.0.0.0"
    env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    env["TF_ENABLE_ONEDNN_OPTS"] = "0"
    
    # Use Popen to keep the process running. @modal.web_server automatically proxies port 8000
    subprocess.Popen(["python", "app.py"], env=env)
