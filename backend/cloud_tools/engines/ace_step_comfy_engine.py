import modal
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append("/root")
sys.path.append("/pkg")
sys.path.append("/")

# Imagem dedicada para o ComfyUI de Áudio (ACE-Step)
audio_comfy_image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("pillow", "requests", "PyYAML", "pytz") \
    .apt_install("git", "wget", "libsndfile1")
    .pip_install(
        "torch==2.5.1",
        "torchvision==0.20.1",
        "torchaudio==2.5.1",
        "comfy-kitchen==0.2.31",
        extra_options="--extra-index-url https://download.pytorch.org/whl/cu121"
    )
    .run_commands(
        "cat << 'EOF' > /tmp/patch.py\n"
        "import glob\n"
        "for f in glob.glob('/usr/local/lib/python3.10/site-packages/comfy_kitchen/**/*.py', recursive=True):\n"
        "    content = open(f).read()\n"
        "    lines = content.split('\\n')\n"
        "    has_future = any(l.startswith('from __future__ import annotations') for l in lines)\n"
        "    if not any(l.startswith('import typing') for l in lines):\n"
        "        if has_future:\n"
        "            idx = next(i for i, l in enumerate(lines) if l.startswith('from __future__ import annotations'))\n"
        "            lines.insert(idx + 1, 'import typing')\n"
        "        else:\n"
        "            lines.insert(0, 'import typing')\n"
        "    content = '\\n'.join(lines)\n"
        "    content = content.replace('list[int]', 'typing.List[int]')\n"
        "    content = content.replace('list[float]', 'typing.List[float]')\n"
        "    content = content.replace('list[bool]', 'typing.List[bool]')\n"
        "    content = content.replace('list[str]', 'typing.List[str]')\n"
        "    content = content.replace('float | None', 'typing.Optional[float]')\n"
        "    open(f, 'w').write(content)\n"
        "EOF",
        "python /tmp/patch.py"
    )
    .pip_install(
        "transformers",
        "accelerate>=0.33.0",
        "huggingface_hub[hf_transfer]",
        "comfy-cli",
        "requests",
        "pillow",
        "fastapi",
        "soundfile"
    )
    .run_commands(
        [
            "comfy --workspace /comfyui install --nvidia",
            "git clone https://github.com/Acly/comfyui-tooling-nodes.git /comfyui/custom_nodes/comfyui-tooling-nodes",
            "git clone https://github.com/ltdrdata/ComfyUI-Manager.git /comfyui/custom_nodes/ComfyUI-Manager",
            "cd /comfyui/custom_nodes/ComfyUI-Manager && pip install -r requirements.txt",
            "git clone https://github.com/billwuhao/ComfyUI_ACE-Step.git /comfyui/custom_nodes/ComfyUI_ACE-Step",
            "cd /comfyui/custom_nodes/ComfyUI_ACE-Step && pip install -r requirements.txt",
            "mkdir -p /comfyui/models/checkpoints",
            "wget -nc -O /comfyui/models/checkpoints/acestep1.5XL_ComfyUI_aio-marduk191.safetensors https://huggingface.co/marduk191/acestep1.5XL_ComfyUI_aio-marduk191/resolve/main/acestep1.5XL_ComfyUI_aio-marduk191.safetensors"
        ]
    )
    .env({
        "HF_HUB_OFFLINE": "0",
        "MODAL_CACHE_BUSTER": "1"
    })
)

apollo_volume = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)

from backend.cloud_tools.modal_app import app
import time
import subprocess
import urllib.request
import json
import base64
import traceback
import glob

@app.cls(image=audio_comfy_image, gpu="A10g", timeout=1800, volumes={"/apollo_volume": apollo_volume}, enable_memory_snapshot=True)
class AceStepComfyEngine:
    @modal.enter(snap=True)
    def load_model(self):
        print("[AceStepComfyEngine] Lancando ComfyUI como subprocesso (porta 8189)...")
        t_boot_start = time.perf_counter()
        
        self.comfy_process = subprocess.Popen(
            ["comfy", "--workspace", "/comfyui", "launch", "--",
             "--listen", "127.0.0.1", "--port", "8189"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )

        server_up = False
        for _ in range(300):
            if self.comfy_process.poll() is not None:
                raise RuntimeError(f"[Boot] ComfyUI encerrou inesperadamente!")
            try:
                with urllib.request.urlopen("http://127.0.0.1:8189/system_stats", timeout=2):
                    server_up = True
                    break
            except Exception:
                time.sleep(1)

        if server_up:
            print(f"[AceStepComfyEngine] ComfyUI porta 8189 pronto em {time.perf_counter() - t_boot_start:.2f}s.")
        else:
            raise RuntimeError("[AceStepComfyEngine] Timeout no boot do ComfyUI.")

    @modal.method()
    def generate(self, style_tags: str, lyrics: str, length_seconds: int = 30, cfg: float = 7.0, steps: int = 40, denoise: float = 1.0) -> dict:
        t0 = time.time()
        print(f"[AceStepComfyEngine] Iniciando requisicao ACE-Step. Length: {length_seconds}s, CFG: {cfg}, Steps: {steps}, Denoise: {denoise}")
        print(f"[AceStepComfyEngine] Estilo: {style_tags}")
        print(f"[AceStepComfyEngine] Letras:\n{lyrics}")
        
        # Limpar outputs antigos para evitar pegar áudio velho
        os.system("rm -f /comfyui/output/*.wav")
        
        try:
            # Base workflow template do ACE-Step
            workflow = {
              "3": {
                "inputs": {
                  "seed": int(time.time()),
                  "steps": steps,
                  "cfg": cfg,
                  "sampler_name": "euler",
                  "scheduler": "simple",
                  "denoise": denoise,
                  "model": ["45", 0],
                  "positive": ["14", 0],
                  "negative": ["44", 0],
                  "latent_image": ["17", 0]
                },
                "class_type": "KSampler"
              },
              "14": {
                "inputs": {
                  "tags": style_tags,
                  "lyrics": lyrics,
                  "lyrics_strength": 1.0,
                  "clip": ["40", 1],
                  "bpm": 120,
                  "cfg_scale": 1.0,
                  "top_p": 0.95,
                  "min_p": 0.05,
                  "seed": int(time.time()),
                  "top_k": 50,
                  "language": "pt",
                  "temperature": 0.8,
                  "timesignature": "4",
                  "keyscale": "C major",
                  "duration": length_seconds,
                  "generate_audio_codes": True
                },
                "class_type": "TextEncodeAceStepAudio1.5"
              },
              "17": {
                "inputs": {
                  "seconds": length_seconds,
                  "batch_size": 1
                },
                "class_type": "EmptyAceStep1.5LatentAudio"
              },
              "18": {
                "inputs": {
                  "samples": ["3", 0],
                  "vae": ["40", 2]
                },
                "class_type": "VAEDecodeAudio"
              },
              "19": {
                "inputs": {
                  "filename_prefix": "audio/ComfyUI",
                  "audio": ["18", 0]
                },
                "class_type": "SaveAudio"
              },
              "40": {
                "inputs": {
                  "ckpt_name": "acestep1.5XL_ComfyUI_aio-marduk191.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
              },
              "44": {
                "inputs": {
                  "conditioning": ["14", 0]
                },
                "class_type": "ConditioningZeroOut"
              },
              "45": {
                "inputs": {
                  "shift": 5.0,
                  "model": ["40", 0]
                },
                "class_type": "ModelSamplingAuraFlow"
              }
            }

            payload = json.dumps({"prompt": workflow}).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=payload, headers={"Content-Type": "application/json"})
            
            try:
                resp = urllib.request.urlopen(req)
                prompt_id = json.loads(resp.read().decode("utf-8"))["prompt_id"]
            except urllib.error.HTTPError as e:
                return {"status": "error", "message": f"Erro ComfyUI (HTTP {e.code}): {e.read().decode('utf-8')}"}
                
            start_wait = time.time()
            while True:
                if time.time() - start_wait > 600:
                    return {"status": "error", "message": "Timeout no processamento ComfyUI"}
                try:
                    hist_resp = urllib.request.urlopen(f"http://127.0.0.1:8189/history/{prompt_id}", timeout=10)
                    hist_data = json.loads(hist_resp.read().decode("utf-8"))
                    if prompt_id in hist_data:
                        # Processo terminou!
                        print("[AceStepComfyEngine] Processamento concluído! Procurando arquivo de saída...")
                        out_data = hist_data[prompt_id].get("outputs", {})
                        
                        # Procurar por chaves 'audio' em todos os outputs caso o id mude
                        audio_filename = None
                        subfolder = ""
                        for node_id, node_out in out_data.items():
                            if "audio" in node_out and len(node_out["audio"]) > 0:
                                audio_filename = node_out["audio"][0].get("filename")
                                subfolder = node_out["audio"][0].get("subfolder", "")
                                break
                        
                        if not audio_filename:
                            # Tenta pelo fallback antigo
                            audio_files = glob.glob("/comfyui/output/**/*.*", recursive=True)
                            if audio_files:
                                latest = max(audio_files, key=os.path.getctime)
                                audio_filename = os.path.basename(latest)
                                subfolder = os.path.dirname(latest).replace("/comfyui/output", "").strip("/")

                        if audio_filename:
                            filepath = os.path.join("/comfyui/output", subfolder, audio_filename)
                            if os.path.exists(filepath):
                                with open(filepath, "rb") as out_f:
                                    b64_out = base64.b64encode(out_f.read()).decode("utf-8")
                                return {
                                    "status": "success",
                                    "audio_base64": b64_out,
                                    "render_time_seconds": round(time.time() - t0, 2),
                                    "format": audio_filename.split('.')[-1]
                                }
                        
                        return {"status": "error", "message": f"Nenhum arquivo de áudio encontrado. Outputs: {json.dumps(out_data)}"}
                except Exception as ex:
                    pass
                time.sleep(2)
        except Exception as e:
            err = traceback.format_exc()
            return {"status": "error", "message": str(e), "traceback": err}
