import modal
import os

flux2_comfy_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "libgl1", "libglib2.0-0")
    .pip_install(
        "torch==2.4.0",
        "torchvision==0.19.0",
        "torchaudio==2.4.0",
        "xformers==0.0.27.post2",
        extra_options="--index-url https://download.pytorch.org/whl/cu121"
    )
    .pip_install(
        "transformers",
        "accelerate>=0.33.0",
        "huggingface_hub[hf_transfer]",
        "comfy-cli",
        "requests",
        "pillow"
    )
    .add_local_file("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/image_flux2/image_flux2 .json", "/tmp/workflow.json", copy=True)
    .run_commands(
        [
            "comfy --workspace /comfyui install --nvidia",
            "comfy --workspace /comfyui node install comfyui-tooling-nodes",
            "comfy --workspace /comfyui node install ComfyUI-Manager",
            "comfy --workspace /comfyui node install-deps --workflow /tmp/workflow.json"
        ]
    )
    .env({
        "HF_HUB_OFFLINE": "0",
        "TRANSFORMERS_OFFLINE": "0",
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
        "MODAL_CACHE_BUSTER": "2"   # nao alterar — evita rebuild Docker desnecessario
    })
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

from backend.cloud_tools.modal_app import app

from contextlib import contextmanager

@contextmanager
def force_cpu_during_snapshot():
    import torch
    orig_is_available = getattr(torch.cuda, "is_available", lambda: False)
    orig_current_device = getattr(torch.cuda, "current_device", lambda: torch.device("cpu"))

    torch.cuda.is_available = lambda: False
    torch.cuda.current_device = lambda: torch.device("cpu")
    try:
        yield
    finally:
        torch.cuda.is_available = orig_is_available
        torch.cuda.current_device = orig_current_device


@app.function(
    image=flux2_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=3600
)
def download_comfy_models():
    import os
    print("Iniciando download dos modelos do Flux.2 para o ComfyUI Volume...")
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors --relative-path models/vae --set-hf-api-token $HF_TOKEN")
    print("Download finalizado!")


# ============================================================
# Flux2ComfyEngine_V2 — IMG2IMG via ComfyUI HTTP subprocess
# PADRAO IDENTICO ao Flux2Txt2ImgEngine (que funciona)
# O ExperimentalComfyServer in-process corrompía o VAEEncode
# ============================================================
@app.cls(
    gpu="H100",
    image=flux2_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    scaledown_window=60,
    timeout=600,
    max_containers=5,
    enable_memory_snapshot=True
)
class Flux2ComfyEngine_V2:
    FORCE_REBUILD = 14  # bump para invalidar snapshot antigo com ExperimentalComfyServer

    @modal.enter(snap=True)
    def load_model(self):
        import subprocess
        import urllib.request
        import time
        import sys

        yaml_content = (
            "modal:\n"
            "  base_path: /comfyui_models\n"
            "  checkpoints: checkpoints\n"
            "  loras: loras\n"
            "  vae: vae\n"
            "  clip: clip\n"
            "  unet: unet\n"
            "  controlnet: controlnet\n"
        )
        with open("/comfyui/extra_model_paths.yaml", "w") as f:
            f.write(yaml_content)

        # MESMO PADRAO DO Flux2Txt2ImgEngine: subprocesso separado + HTTP API
        # O ExperimentalComfyServer in-process corrompe o VAEEncode do img2img
        with force_cpu_during_snapshot():
            print("[Flux2ComfyEngine_V2] Lancando ComfyUI como subprocesso (porta 8189)...")
            self.comfy_process = subprocess.Popen(
                ["comfy", "--workspace", "/comfyui", "launch", "--",
                 "--listen", "127.0.0.1", "--port", "8189", "--highvram"],
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )

            # Aguardar servidor pronto (snapshot captura estado estavel)
            server_up = False
            for _ in range(180):
                try:
                    with urllib.request.urlopen("http://127.0.0.1:8189/system_stats", timeout=2):
                        server_up = True
                        break
                except Exception:
                    time.sleep(1)

            if server_up:
                print("[Flux2ComfyEngine_V2] SNAPSHOT V_HTTP OK! ComfyUI porta 8189 pronto.")
            else:
                raise RuntimeError("[Flux2ComfyEngine_V2] Timeout no boot do ComfyUI para snapshot.")

    @modal.method()
    def generate(self, prompt: str, aspect_ratio: str = "horizontal", style: str = None, **kwargs) -> dict:
        import urllib.request
        import json
        import time
        import traceback
        import base64
        import os
        import io
        from PIL import Image as PILImage

        t0 = time.time()
        print(f"[Flux2ComfyEngine_V2] Request: {prompt[:60]}... | Formato: {aspect_ratio} | Estilo: {style}")

        seed = kwargs.get("seed", 42)

        try:
            # 1. Salvar imagem de entrada em /comfyui/input/ como PNG valido
            if kwargs.get("input_image_b64"):
                img_data = base64.b64decode(kwargs["input_image_b64"])
                pil_img = PILImage.open(io.BytesIO(img_data)).convert("RGB")
                input_image_path = "/comfyui/input/image_flux2_input_image.png"
                os.makedirs("/comfyui/input", exist_ok=True)
                pil_img.save(input_image_path, format="PNG")
                saved_size = os.path.getsize(input_image_path)
                print(f"[Flux2ComfyEngine_V2] Imagem entrada: {pil_img.size} | {saved_size} bytes | {input_image_path}")
            else:
                print("[Flux2ComfyEngine_V2] AVISO: sem input_image_b64")

            # 2. Carregar workflow e atualizar nos (por class_type — robusto a mudancas de IDs)
            with open("/tmp/workflow.json", "r", encoding="utf-8") as f:
                workflow = json.load(f)
            print(f"[Flux2ComfyEngine_V2] Workflow carregado: {len(workflow)} nos")

            nodes_updated = []
            for node_id, node in workflow.items():
                ct = node.get("class_type", "")
                if ct == "CLIPTextEncode" and "text" in node["inputs"]:
                    node["inputs"]["text"] = prompt
                    nodes_updated.append(f"CLIPTextEncode({node_id})")
                elif ct == "RandomNoise":
                    node["inputs"]["noise_seed"] = seed % 1_000_000_000_000_000
                    nodes_updated.append(f"RandomNoise({node_id})=seed:{seed}")
            
            if style:
                print(f"[Flux2ComfyEngine_V2] ✨ Estilo Lora selecionado: '{style}'. (A Injeção do LoraLoader no Grafo JSON será ativada após download dos pesos .safetensors no volume)")
                
            print(f"[Flux2ComfyEngine_V2] Nos atualizados: {nodes_updated}")

            # 3. Submeter workflow via HTTP ao ComfyUI local
            payload = json.dumps({"prompt": workflow}).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8189/prompt",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            resp = urllib.request.urlopen(req)
            resp_data = json.loads(resp.read().decode("utf-8"))
            prompt_id = resp_data["prompt_id"]
            print(f"[Flux2ComfyEngine_V2] Job submetido: {prompt_id}")

            # 4. Polling ate concluir
            while True:
                try:
                    hist_resp = urllib.request.urlopen(
                        f"http://127.0.0.1:8189/history/{prompt_id}", timeout=10
                    )
                    hist_data = json.loads(hist_resp.read().decode("utf-8"))
                    if prompt_id in hist_data:
                        outputs = hist_data[prompt_id].get("outputs", {})
                        if outputs:
                            out_node = list(outputs.keys())[0]
                            images = outputs[out_node].get("images", [])
                            if images:
                                out_filename = images[0]["filename"]
                                out_path = os.path.join("/comfyui/output", out_filename)
                                with open(out_path, "rb") as out_f:
                                    b64_out = base64.b64encode(out_f.read()).decode("utf-8")

                                render_time = time.time() - t0
                                check_img = PILImage.open(out_path)
                                sample_px = list(check_img.getdata())[:5]
                                print(f"[Flux2ComfyEngine_V2] Output: {check_img.size} | pixels[0:5]={sample_px}")
                                print(f"[Flux2ComfyEngine_V2] Geracao OK em {render_time:.2f}s")
                                return {
                                    "status": "success",
                                    "image_base64": b64_out,
                                    "render_time_seconds": round(render_time, 2),
                                    "engine": "FLUX-2-IMG2IMG-HTTP-H100"
                                }
                except Exception:
                    pass
                time.sleep(2)

        except Exception as e:
            err = traceback.format_exc()
            print(f"[Flux2ComfyEngine_V2] ERROR: {err}")
            return {"status": "error", "message": str(e), "traceback": err}
