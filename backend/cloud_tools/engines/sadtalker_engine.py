import modal
import os
import subprocess
import base64
import uuid
import time

# Baixador de modelos (Roda durante o build da imagem)
def download_sadtalker_models():
    print("[Build] Baixando modelos do SadTalker...")
    import urllib.request
    
    base_url = "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/"
    models = [
        "mapping_00109-model.pth.tar",
        "mapping_00229-model.pth.tar",
        "SadTalker_V0.0.2_256.safetensors",
        "SadTalker_V0.0.2_512.safetensors"
    ]
    
    os.makedirs("/SadTalker/checkpoints", exist_ok=True)
    for model in models:
        path = f"/SadTalker/checkpoints/{model}"
        if not os.path.exists(path):
            print(f"Baixando {model}...")
            urllib.request.urlretrieve(base_url + model, path)
            
    # Baixar GFPGAN e outros
    os.makedirs("/SadTalker/gfpgan/weights", exist_ok=True)
    gfpgan_url = "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth"
    urllib.request.urlretrieve(gfpgan_url, "/SadTalker/gfpgan/weights/GFPGANv1.4.pth")
    print("[Build] Modelos baixados com sucesso!")

# Configuração da Imagem do SadTalker
sadtalker_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg", "libsm6", "libxext6", "wget", "cmake", "g++")
    .pip_install(
        "torch==2.0.1",
        "torchvision==0.15.2",
        "torchaudio==2.0.2",
        extra_options="--index-url https://download.pytorch.org/whl/cu118"
    )
    .run_commands(
        "git clone https://github.com/OpenTalker/SadTalker.git /SadTalker",
        "cd /SadTalker && pip install -r requirements.txt",
        "pip install gfpgan xformers==0.0.20 imageio-ffmpeg"
    )
    .run_function(download_sadtalker_models)
)

try:
    from backend.cloud_tools.modal_app import app
except ImportError:
    app = modal.App("dummy")

@app.cls(gpu="L4", timeout=1200, image=sadtalker_image)
class SadTalkerEngine:
    
    @modal.method()
    def generate(self, image_base64: str, audio_base64: str, enhancer: str = "gfpgan", preprocess: str = "crop", still: bool = True) -> dict:
        print("[SadTalkerEngine] Iniciando geração Lipsync...")
        t0 = time.time()
        
        req_id = str(uuid.uuid4())[:8]
        img_path = f"/tmp/input_img_{req_id}.png"
        aud_path = f"/tmp/input_aud_{req_id}.wav"
        out_dir = f"/tmp/sadtalker_out_{req_id}"
        
        # Limpar base64 headers se houver
        if "," in image_base64: image_base64 = image_base64.split(",")[1]
        if "," in audio_base64: audio_base64 = audio_base64.split(",")[1]
            
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(image_base64))
            
        with open(aud_path, "wb") as f:
            f.write(base64.b64decode(audio_base64))
            
        print("[SadTalkerEngine] Arquivos salvos. Rodando inferência...")
        
        cmd = [
            "python", "/SadTalker/inference.py",
            "--driven_audio", aud_path,
            "--source_image", img_path,
            "--result_dir", out_dir,
            "--preprocess", preprocess
        ]
        
        if enhancer:
            cmd.extend(["--enhancer", enhancer])
        if still:
            cmd.append("--still")
            
        try:
            # Roda o script de inferencia do SadTalker
            subprocess.check_call(cmd, cwd="/SadTalker")
            
            # Achar o arquivo de saida
            result_video = None
            for root, dirs, files in os.walk(out_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        result_video = os.path.join(root, file)
                        break
                        
            if not result_video:
                return {"status": "error", "message": "Video não gerado."}
                
            with open(result_video, "rb") as f:
                vid_b64 = base64.b64encode(f.read()).decode("utf-8")
                
            render_time = time.time() - t0
            print(f"[SadTalkerEngine] Sucesso! Tempo: {render_time:.2f}s")
            
            return {
                "status": "success",
                "video_base64": vid_b64,
                "render_time_seconds": round(render_time, 2)
            }
            
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Falha no SadTalker: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

@app.local_entrypoint()
def test_sadtalker():
    print("SadTalkerEngine configurada!")
