import modal
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append("/root")
sys.path.append("/pkg")
sys.path.append("/")

# Imagem "Gorda" (Omni-Image) com nós populares
universal_comfy_image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("pillow", "requests", "PyYAML", "pytz") \
    .apt_install("git", "libgl1", "libglib2.0-0", "wget")
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
        "pillow",
        "fastapi"
    )
    .run_commands(
        [
            "comfy --workspace /comfyui install --nvidia",
            "comfy --workspace /comfyui node install comfyui-tooling-nodes",
            "comfy --workspace /comfyui node install ComfyUI-Manager",
            "comfy --workspace /comfyui node install ComfyUI-VideoHelperSuite",
            "git clone https://github.com/lldacing/ComfyUI_PuLID_Flux_ll.git /comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll && cd /comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll && pip install -r requirements.txt && pip install facenet-pytorch --no-deps && sed -i 's/_root = os.path.expanduser(root)/import os\\n    _root = os.path.expanduser(root)/g' pulidflux.py",
            "comfy --workspace /comfyui node install https://github.com/TTPlanetPig/Comfyui_TTP_Toolset",
            "comfy --workspace /comfyui node install https://github.com/yolain/ComfyUI-Easy-Use",
            "comfy --workspace /comfyui node install https://github.com/rgthree/rgthree-comfy",
            "comfy --workspace /comfyui node install https://github.com/kijai/ComfyUI-KJNodes",
            "comfy --workspace /comfyui node install https://github.com/ltdrdata/ComfyUI-Impact-Pack",
            "git clone https://github.com/Ryuukeisyou/comfyui_face_parsing.git /comfyui/custom_nodes/comfyui_face_parsing && cd /comfyui/custom_nodes/comfyui_face_parsing && sed -i -E '/^torch([=><].*)?$/d' requirements.txt && pip install -r requirements.txt && mkdir -p /comfyui/models/face_parsing && wget -qO /comfyui/models/face_parsing/preprocessor_config.json \"https://huggingface.co/jonathandinu/face-parsing/resolve/main/preprocessor_config.json\" && wget -qO /comfyui/models/face_parsing/model.safetensors \"https://huggingface.co/jonathandinu/face-parsing/resolve/main/model.safetensors\" && wget -qO /comfyui/models/face_parsing/config.json \"https://huggingface.co/jonathandinu/face-parsing/resolve/main/config.json\" && mkdir -p /comfyui/models/ultralytics/bbox && wget -qO /comfyui/models/ultralytics/bbox/face_yolov8n.pt \"https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8n.pt\" && wget -qO /comfyui/models/ultralytics/bbox/face_yolov8s.pt \"https://huggingface.co/Bingsu/adetailer/resolve/main/face_yolov8s.pt\"",
            "git clone https://github.com/cubiq/ComfyUI_essentials.git /comfyui/custom_nodes/ComfyUI_essentials && cd /comfyui/custom_nodes/ComfyUI_essentials && sed -i -E '/^torch([=><].*)?$/d' requirements.txt && pip install -r requirements.txt",
            "git clone https://github.com/chflame163/ComfyUI_LayerStyle.git /comfyui/custom_nodes/ComfyUI_LayerStyle && cd /comfyui/custom_nodes/ComfyUI_LayerStyle && sed -i -E '/^torch([=><].*)?$/d' requirements.txt && pip install -r requirements.txt",
            "git clone https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler.git /comfyui/custom_nodes/ComfyUI-SeedVR2_VideoUpscaler && cd /comfyui/custom_nodes/ComfyUI-SeedVR2_VideoUpscaler && sed -i -E '/^torch([=><].*)?$/d' requirements.txt && pip install -r requirements.txt",
            "git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git /comfyui/custom_nodes/ComfyUI_UltimateSDUpscale",
            "pip install --upgrade diffusers==0.31.0",
            "comfy --workspace /comfyui node install https://github.com/WASasquatch/was-node-suite-comfyui"
        ]
    )
    .add_local_file(
        local_path=os.path.join(os.path.dirname(__file__), "pulid_ll_patch.py"),
        remote_path="/pulid_ll_patch.py",
        copy=True,
    )
    .run_commands(["python /pulid_ll_patch.py"])
    .env({
        "HF_HUB_OFFLINE": "0",
        "TRANSFORMERS_OFFLINE": "0",
        "HF_HUB_ENABLE_HF_TRANSFER": "1",
        "MODAL_CACHE_BUSTER": "14"
    })
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
apollo_volume = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)

from backend.cloud_tools.modal_app import app
from contextlib import contextmanager
import time

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


@app.cls(
    gpu="H100",
    image=universal_comfy_image,
    volumes={"/comfyui_models": comfy_volume, "/apollo_volume": apollo_volume},
    scaledown_window=60,
    timeout=1200,
    max_containers=5,
    enable_memory_snapshot=True
)
class UniversalComfyEngine:
    FORCE_REBUILD = 3

    @modal.enter()
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
            "  pulid: pulid\n"
            "  clip_vision: clip_vision\n"
            "  style_models: style_models\n"
            "  upscale_models: upscale_models\n"
            "apollo:\n"
            "  base_path: /apollo_volume/models\n"
            "  unet: diffusion_models\n"
            "  clip: text_encoders\n"
            "  vae: vae\n"
            "  upscale_models: upscale_models\n"
        )
        with open("/comfyui/extra_model_paths.yaml", "w") as f:
            f.write(yaml_content)
        subprocess.run("mkdir -p /comfyui/models/insightface/models", shell=True)
        subprocess.run("ln -sf /comfyui_models/insightface/models/antelopev2 /comfyui/models/insightface/models/antelopev2", shell=True)

        print("[UniversalComfyEngine] Preparando ambiente e restaurando modelos no volume...")
        
        # Garante que a pasta upscale_models existe no volume
        os.makedirs("/comfyui_models/upscale_models", exist_ok=True)
        
        # Baixa o 4x-UltraSharp se não existir
        model_path = "/comfyui_models/upscale_models/4x-UltraSharp.pth"
        if not os.path.exists(model_path):
            print(f"[UniversalComfyEngine] Baixando 4x-UltraSharp para o volume {model_path}...")
            import urllib.request
            urllib.request.urlretrieve("https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth", model_path)
            print("[UniversalComfyEngine] Download concluído.")
            
        print("[UniversalComfyEngine] Lancando ComfyUI como subprocesso (porta 8189)...")
        t_boot_start = time.perf_counter()
        
        # INJETAR O PATCH DO GQA DIRETAMENTE NOS CUSTOM NODES DO COMFYUI ANTES DO BOOT
        patch_code = """import torch.nn.functional as F
if not hasattr(F, '_original_sdpa'):
    F._original_sdpa = F.scaled_dot_product_attention
    def patched_sdpa(q, k, v, attn_mask=None, dropout_p=0.0, is_causal=False, scale=None, **kwargs):
        gqa = kwargs.pop('enable_gqa', None)
        if gqa or q.shape[1] != k.shape[1]:
            if q.shape[1] % k.shape[1] == 0:
                groups = q.shape[1] // k.shape[1]
                if groups > 1:
                    k = k.repeat_interleave(groups, dim=1)
                    v = v.repeat_interleave(groups, dim=1)
        return F._original_sdpa(q, k, v, attn_mask=attn_mask, dropout_p=dropout_p, is_causal=is_causal, scale=scale, **kwargs)
    F.scaled_dot_product_attention = patched_sdpa

try:
    import comfy.ops
    comfy.ops.scaled_dot_product_attention = patched_sdpa
except Exception:
    pass
print("[PATCH] GQA Patch aplicado com sucesso no ComfyUI com repeat_interleave!")
"""
        try:
            with open("/comfyui/custom_nodes/patch_gqa.py", "w") as f:
                f.write(patch_code)
        except Exception as e:
            print(f"[UniversalComfyEngine] Erro ao gravar patch: {e}")
            
        self.comfy_process = subprocess.Popen(
            ["comfy", "--workspace", "/comfyui", "launch", "--",
             "--listen", "127.0.0.1", "--port", "8189", "--highvram"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )

        server_up = False
        for _ in range(180):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8189/system_stats", timeout=2):
                    server_up = True
                    break
            except Exception:
                time.sleep(1)

        if server_up:
            t2_boot_time = time.perf_counter() - t_boot_start
            print(f"[UniversalComfyEngine] SNAPSHOT V_HTTP OK! ComfyUI porta 8189 pronto em {t2_boot_time:.2f}s.")
        else:
            raise RuntimeError("[UniversalComfyEngine] Timeout no boot do ComfyUI para snapshot.")

    @modal.method()
    def fetch_file(self, path):
        with open(path, "r") as f:
            return f.read()

    @modal.method()
    def generate(self, workflow_json_string: str, prompt: str = None, input_image_b64: str = None, regional_prompts: list = None, is_upscale: bool = False, denoise: float = None, **kwargs) -> dict:
        return self._generate(workflow_json_string, prompt, input_image_b64, regional_prompts, is_upscale, denoise, **kwargs)

    def _generate(self, workflow_json_string: str, prompt: str = None, input_image_b64: str = None, regional_prompts: list = None, is_upscale: bool = False, denoise: float = None, **kwargs) -> dict:
        import urllib.error
        import urllib.request
        import json
        import time
        import traceback
        import base64
        import os
        import io
        from PIL import Image as PILImage

        t0 = time.time()
        print("[UniversalComfyEngine] Iniciando requisicao Universal...")

        seed = kwargs.get("seed", int(time.time() * 1000) % 4294967295)

        try:
            import torch.nn.functional as F
            if not hasattr(F, '_original_sdpa'):
                F._original_sdpa = F.scaled_dot_product_attention
                def patched_sdpa(q, k, v, attn_mask=None, dropout_p=0.0, is_causal=False, scale=None, **kwargs):
                    kwargs.pop('enable_gqa', None)
                    return F._original_sdpa(q, k, v, attn_mask=attn_mask, dropout_p=dropout_p, is_causal=is_causal, scale=scale, **kwargs)
                F.scaled_dot_product_attention = patched_sdpa
        except Exception:
            pass
        try:
            import comfy.ops
            comfy.ops.scaled_dot_product_attention = patched_sdpa
        except Exception:
            pass

            workflow = json.loads(workflow_json_string)

            input_images = kwargs.get("input_images_b64", [])
            if input_image_b64:
                input_images = [input_image_b64]
                
            new_char = kwargs.get("new_character_image_b64")
            if new_char:
                input_images.append(new_char)
                
            has_base = False
            has_char = False
            for node in workflow.values():
                title = node.get("_meta", {}).get("title", "")
                if title == "APOLLO_BASE_IMAGE": has_base = True
                if title == "APOLLO_CHAR_IMAGE": has_char = True

            if has_base and has_char and len(input_images) >= 2:
                print(f"[UniversalComfyEngine] Multi-Pass ativado. Total de imagens (1 Base + {len(input_images)-1} Chars).")
                
                current_base_b64 = input_images[0]
                char_images = input_images[1:]
                
                final_b64 = current_base_b64
                
                for idx, char_b64 in enumerate(char_images):
                    print(f"[UniversalComfyEngine] Multi-Pass: Iteracao {idx+1}/{len(char_images)}")
                    
                    base_data = base64.b64decode(current_base_b64)
                    base_img = PILImage.open(io.BytesIO(base_data)).convert("RGB")
                    base_filename = f"apollo_base_iter_{idx}.png"
                    os.makedirs("/comfyui/input", exist_ok=True)
                    base_img.save(f"/comfyui/input/{base_filename}", format="PNG")
                    
                    char_data = base64.b64decode(char_b64)
                    char_img = PILImage.open(io.BytesIO(char_data)).convert("RGB")
                    char_filename = f"apollo_char_iter_{idx}.png"
                    char_img.save(f"/comfyui/input/{char_filename}", format="PNG")
                    
                    wf_iter = json.loads(workflow_json_string)
                    
                    for node_id, node in wf_iter.items():
                        title = node.get("_meta", {}).get("title", "")
                        if title == "APOLLO_BASE_IMAGE":
                            node["inputs"]["image"] = base_filename
                        if title == "APOLLO_CHAR_IMAGE":
                            node["inputs"]["image"] = char_filename
                        
                        current_iter_prompt = prompt
                        if regional_prompts and len(regional_prompts) > idx:
                            current_iter_prompt = ", ".join(regional_prompts[:idx+1])
                            
                        if ("APOLLO_PROMPT" in title or "Positive Prompt" in title) and current_iter_prompt:
                            for k in node.get("inputs", {}):
                                if isinstance(node["inputs"][k], str) and k in ["text", "string"]:
                                    node["inputs"][k] = current_iter_prompt
                                    break
                        if "inputs" in node:
                            for k in ["noise_seed", "seed"]:
                                if k in node["inputs"]:
                                    node["inputs"][k] = seed + idx
                                    
                    payload = json.dumps({"prompt": wf_iter}).encode("utf-8")
                    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=payload, headers={"Content-Type": "application/json"})
                    try:
                        resp = urllib.request.urlopen(req)
                        prompt_id = json.loads(resp.read().decode("utf-8"))["prompt_id"]
                    except urllib.error.HTTPError as e:
                        body = e.read().decode("utf-8")
                        return {"status": "error", "message": f"Erro ComfyUI (HTTP {e.code}): {body}"}
                    
                    iter_success = False
                    max_wait_secs = 600
                    waited = 0
                    while waited < max_wait_secs:
                        try:
                            hist_resp = urllib.request.urlopen(f"http://127.0.0.1:8189/history/{prompt_id}", timeout=10)
                            hist_data = json.loads(hist_resp.read().decode("utf-8"))
                            if prompt_id in hist_data:
                                outputs = hist_data[prompt_id].get("outputs", {})
                                if outputs:
                                    out_node = list(outputs.keys())[0]
                                    if "images" in outputs[out_node] and len(outputs[out_node]["images"]) > 0:
                                        out_filename = outputs[out_node]["images"][0]["filename"]
                                        out_path = os.path.join("/comfyui/output", out_filename)
                                        with open(out_path, "rb") as out_f:
                                            current_base_b64 = base64.b64encode(out_f.read()).decode("utf-8")
                                            final_b64 = current_base_b64
                                            iter_success = True
                                        break
                                    # outputs existe mas sem imagens ainda — continua esperando
                                # prompt_id nao esta no historico ainda — continua esperando
                        except Exception as poll_err:
                            print(f"[Poll] Erro temporario: {poll_err}")
                        time.sleep(3)
                        waited += 3
                        
                    if not iter_success:
                        return {"error": f"Multi-pass falhou na iteracao {idx+1}"}
                        
                render_time = time.time() - t0
                return {
                    "status": "success",
                    "image_base64": final_b64,
                    "render_time_seconds": round(render_time, 2),
                    "engine": "UNIVERSAL-COMFY-MULTIPASS-H100"
                }

            # Mapeamento explicito das imagens base e char
            base_filename = "apollo_universal_base.png"
            char_filename = "apollo_universal_char.png"
            os.makedirs("/comfyui/input", exist_ok=True)
            
            if input_image_b64:
                img_data = base64.b64decode(input_image_b64)
                pil_img = PILImage.open(io.BytesIO(img_data)).convert("RGB")
            else:
                pil_img = PILImage.new("RGB", (1024, 1024), (255, 255, 255))
            pil_img.save(os.path.join("/comfyui/input", base_filename), format="PNG")
            
            if kwargs.get("new_character_image_b64"):
                img_data = base64.b64decode(kwargs.get("new_character_image_b64"))
                pil_img = PILImage.open(io.BytesIO(img_data)).convert("RGB")
            else:
                pil_img = PILImage.new("RGB", (1024, 1024), (255, 255, 255))
            pil_img.save(os.path.join("/comfyui/input", char_filename), format="PNG")

            if "reference_images" in kwargs and isinstance(kwargs["reference_images"], dict):
                print(f"[UniversalComfyEngine] Recebendo {len(kwargs['reference_images'])} imagens de referencia customizadas...")
                for ref_filename, ref_b64 in kwargs["reference_images"].items():
                    if ref_b64:
                        ref_data = base64.b64decode(ref_b64)
                        ref_img = PILImage.open(io.BytesIO(ref_data)).convert("RGB")
                        ref_img.save(os.path.join("/comfyui/input", ref_filename), format="PNG")
                        print(f"[UniversalComfyEngine] Salvo em /comfyui/input/{ref_filename}")

            nodes_updated = []
            
            # Se for a primeira passagem (sem imagem de entrada), injeta um EmptyLatentImage
            is_first_pass = not kwargs.get("input_image_b64")
            vae_encode_base_id = None
            
            # Encontra o ID do VAE_ENCODE_BASE
            for node_id, node in list(workflow.items()):
                title = str(node.get("_meta", {}).get("title", ""))
                if title == "VAEEncode Base" or node.get("class_type") == "VAEEncode":
                    # Checar se ele usa o APOLLO_BASE_IMAGE
                    inputs = node.get("inputs", {})
                    for k, v in inputs.items():
                        if isinstance(v, list) and len(v) > 0:
                            # Se for o ID do APOLLO_BASE_IMAGE, entao achamos o encode
                            target_node = workflow.get(v[0])
                            if target_node and target_node.get("_meta", {}).get("title") == "APOLLO_BASE_IMAGE":
                                vae_encode_base_id = node_id
                                break

            # Adiciona o node EMPTY_LATENT_BASE se for primeira passagem
            if is_first_pass:
                empty_latent_id = "EMPTY_LATENT_BASE_INJECTED"
                workflow[empty_latent_id] = {
                    "class_type": "EmptyLatentImage",
                    "inputs": {
                        "width": 1024,
                        "height": 1024,
                        "batch_size": 1
                    }
                }

            for node_id, node in list(workflow.items()):
                title = str(node.get("_meta", {}).get("title", ""))
                
                # Redireciona inputs que usam VAE_ENCODE_BASE para EMPTY_LATENT_BASE
                if is_first_pass and vae_encode_base_id:
                    for input_key, input_val in node.get("inputs", {}).items():
                        if isinstance(input_val, list) and len(input_val) > 0 and input_val[0] == vae_encode_base_id:
                            node["inputs"][input_key] = [empty_latent_id, 0]
                            nodes_updated.append(f"Redirected_{input_key}_to_EmptyLatent_{node_id}")

                # Injeta a base image
                if title == "APOLLO_BASE_IMAGE":
                    node["inputs"]["image"] = base_filename
                    nodes_updated.append(f"Mapped_Base_to_{node_id}")
                    
                # Injeta a char image
                if title == "APOLLO_CHAR_IMAGE":
                    node["inputs"]["image"] = char_filename
                    nodes_updated.append(f"Mapped_Char_to_{node_id}")
                    
                # Input generico antigo para retrocompatibilidade
                if ("APOLLO_INPUT_IMAGE" in title or (node.get("class_type") == "LoadImage" and title == "Load Image")) and base_filename:
                    if "image" in node.get("inputs", {}):
                        node["inputs"]["image"] = base_filename
                        nodes_updated.append(f"Base_Image_Injected({node_id})")

                if ("APOLLO_PROMPT" in title or "Positive Prompt" in title or "Prompt" in title) and prompt:
                    for k in node.get("inputs", {}):
                        if isinstance(node["inputs"][k], str) and k in ["text", "string"]:
                            node["inputs"][k] = prompt
                            nodes_updated.append(f"PROMPT_UPDATED({node_id})")
                            break
                if "inputs" in node:
                    for k in ["noise_seed", "seed"]:
                        if k in node["inputs"]:
                            node["inputs"][k] = seed
                            nodes_updated.append(f"Seed({node_id})")
                            
                # Upscale override
                if is_upscale and (node.get("class_type") == "KSampler" or "Sampler" in str(node.get("class_type", ""))):
                    if "denoise" in node.get("inputs", {}):
                        node["inputs"]["denoise"] = denoise if denoise is not None else 0.25
                        nodes_updated.append(f"Upscale_Denoise_Set({node_id})")
            
            # Bypass logic for Upscale
            if is_upscale:
                bypass_class_types = ["ApplyPulidFlux", "ReferenceLatent"]
                bypassed_mapping = {} # old_node_id -> input_it_should_forward
                
                # 1. Identify nodes to bypass and what they forward
                for node_id, node in list(workflow.items()):
                    if node.get("class_type") in bypass_class_types:
                        # Find the first input that is a list (link) and is likely the main model/latent
                        # Usually "model", "latent", etc.
                        for key in ["model", "latent", "conditioning"]:
                            if key in node.get("inputs", {}) and isinstance(node["inputs"][key], list):
                                bypassed_mapping[node_id] = node["inputs"][key]
                                nodes_updated.append(f"Bypassing_{node_id}({node.get('class_type')})")
                                break
                                
                # 2. Reroute connections
                for node_id, node in list(workflow.items()):
                    for input_key, input_val in node.get("inputs", {}).items():
                        if isinstance(input_val, list) and len(input_val) > 0:
                            target_id = str(input_val[0])
                            if target_id in bypassed_mapping:
                                node["inputs"][input_key] = bypassed_mapping[target_id]
                                nodes_updated.append(f"Rerouted_{input_key}_in_{node_id}")
            
            payload = json.dumps({"prompt": workflow}).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=payload, headers={"Content-Type": "application/json"})
            t_submit = time.perf_counter()
            try:
                resp = urllib.request.urlopen(req)
                prompt_id = json.loads(resp.read().decode("utf-8"))["prompt_id"]
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8")
                return {"status": "error", "message": f"Erro ComfyUI (HTTP {e.code}): {body}"}

            # Wait for execution
            start_wait = time.time()
            while True:
                if time.time() - start_wait > 3600:  # 60 minutes max
                    return {"status": "error", "message": "Timeout de 60 minutos aguardando ComfyUI."}
                try:
                    hist_resp = urllib.request.urlopen(f"http://127.0.0.1:8189/history/{prompt_id}", timeout=10)
                    hist_data = json.loads(hist_resp.read().decode("utf-8"))
                    if prompt_id in hist_data:
                        outputs = hist_data[prompt_id].get("outputs", {})
                        if outputs:
                            # Prioritize SaveImage nodes
                            save_node_ids = [nid for nid, n in workflow.items() if n.get("class_type") == "SaveImage"]
                            out_node = None
                            for nid in save_node_ids:
                                if nid in outputs:
                                    out_node = nid
                                    break
                            
                            # Fallback to first available output
                            if not out_node:
                                out_node = list(outputs.keys())[0]
                                
                            if "images" in outputs[out_node] and len(outputs[out_node]["images"]) > 0:
                                out_filename = outputs[out_node]["images"][0]["filename"]
                                out_path = os.path.join("/comfyui/output", out_filename)
                                with open(out_path, "rb") as out_f:
                                    b64_out = base64.b64encode(out_f.read()).decode("utf-8")
                                    try:
                                        import shutil
                                        shutil.copy(out_path, "/apollo_volume/multipass_final.png")
                                        print("Salvo no volume com sucesso!")
                                    except Exception as e:
                                        print(f"Erro ao salvar no volume: {e}")
                                render_time = time.time() - t0
                                return {
                                    "status": "success",
                                    "image_base64": b64_out,
                                    "render_time_seconds": round(render_time, 2),
                                    "engine": "UNIVERSAL-COMFY-H100"
                                }
                            
                            # Tentar extrair o erro do status
                            status_info = hist_data[prompt_id].get("status", {})
                            messages = status_info.get("messages", [])
                            error_details = []
                            for msg in messages:
                                if isinstance(msg, list) and len(msg) > 1 and msg[0] == "execution_error":
                                    error_details.append(str(msg[1]))
                                elif isinstance(msg, dict) and msg.get("type") == "execution_error":
                                    error_details.append(str(msg))
                            
                            error_str = " | ".join(error_details) if error_details else "Execução falhou ou não retornou outputs."
                            
                            return {"status": "error", "message": error_str}
                    else:
                        # Check queue
                        q_resp = urllib.request.urlopen("http://127.0.0.1:8189/queue", timeout=10)
                        q_data = json.loads(q_resp.read().decode("utf-8"))
                        pending = q_data.get("queue_running", []) + q_data.get("queue_pending", [])
                        is_in_queue = any(q[1] == prompt_id for q in pending)
                        if not is_in_queue:
                            return {"status": "error", "message": "Prompt falhou silenciosamente (desapareceu da fila e não está no histórico)."}
                except Exception as ex:
                    print(f"Polling warning: {ex}")
                time.sleep(2)

        except Exception as e:
            err = traceback.format_exc()
            print(f"[UniversalComfyEngine] ERROR: {err}")
            return {"status": "error", "message": str(e), "traceback": err}

    @modal.method()
    def multi_pass_generation(self, script: dict) -> dict:
        import time
        import traceback
        
        t0 = time.time()
        print(f'[UniversalComfyEngine] Iniciando Multi-Pass Generation...')
        
        try:
            workflow_json_string = script.get('workflow_json_string')
            etapas = script.get('etapas', [])
            
            if not workflow_json_string or not etapas:
                return {"status": "error", "message": "Faltando workflow_json_string ou etapas no script"}
                
            current_image_b64 = script.get('base_image_b64')
            
            for i, etapa in enumerate(etapas):
                print(f'[UniversalComfyEngine] Processando etapa {i+1}/{len(etapas)}')
                prompt = etapa.get('prompt')
                character_image_b64 = etapa.get('image_b64')
                is_upscale = etapa.get('is_upscale', False)
                denoise = etapa.get('denoise', None)
                etapa_workflow = etapa.get('workflow_json_string', workflow_json_string)
                
                result = self._generate(
                    workflow_json_string=etapa_workflow,
                    prompt=prompt,
                    input_image_b64=current_image_b64,
                    new_character_image_b64=character_image_b64,
                    is_upscale=is_upscale,
                    denoise=denoise
                )
                
                if result.get('status') == 'success':
                    current_image_b64 = result.get('image_base64')
                else:
                    return {"status": "error", "message": f"Falha na etapa {i+1}: {result.get('message')}"}
                    
            render_time = time.time() - t0
            return {
                "status": "success",
                "image_base64": current_image_b64,
                "render_time_seconds": round(render_time, 2),
                "engine": "UNIVERSAL-COMFY-H100-MULTIPASS"
            }
            
        except Exception as e:
            err = traceback.format_exc()
            print(f"[UniversalComfyEngine] MULTI-PASS ERROR: {err}")
            return {"status": "error", "message": str(e), "traceback": err}

    @modal.method()
    def generate(self, workflow_json_string: str, prompt: str = None, input_image_b64: str = None, regional_prompts: list = None, **kwargs) -> dict:
        return self._generate(workflow_json_string, prompt, input_image_b64, regional_prompts, **kwargs)

    @modal.method()
    def convert_ui_to_api(self, ui_json_string: str) -> dict:
        """
        Converts a UI-format ComfyUI workflow (nodes & links) to the API-format
        using comfy-cli's --print-prompt feature.
        Requires ComfyUI to be running so it can fetch /object_info.
        """
        import subprocess
        import json
        import os
        
        # Start ComfyUI if not running
        # ComfyUI is already started by load_model() via @modal.enter()
        
        # Save the UI JSON to a temporary file
        temp_ui_path = "/tmp/ui_workflow.json"
        with open(temp_ui_path, "w", encoding="utf-8") as f:
            f.write(ui_json_string)
            
        print("[UniversalComfyEngine] Converting UI JSON to API JSON using comfy-cli...")
        try:
            # comfy run --workflow /tmp/ui_workflow.json --print-prompt
            result = subprocess.run(
                ["comfy", "run", "--workflow", temp_ui_path, "--print-prompt", "--host", "127.0.0.1", "--port", "8189"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # The output should be the API JSON
            api_json_str = result.stdout.strip()
            
            # Sometimes comfy-cli prints other logs to stdout. Let's try to parse it.
            # We will extract the last valid JSON object from the output.
            api_json = json.loads(api_json_str)
            return {"status": "success", "api_json": api_json}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"comfy-cli failed: {e.stderr}"}
        except Exception as e:
            # If json.loads fails, it might be because of extra text.
            return {"status": "error", "message": str(e), "raw_output": api_json_str if 'api_json_str' in locals() else ""}

from fastapi import FastAPI, Request
web_app = FastAPI()

@web_app.post("/{endpoint_path:path}")
async def handle_request(endpoint_path: str, request: Request):
    data = await request.json()
    engine = UniversalComfyEngine()
    script = data.get("script", {})
    if not script:
        return {"status": "error", "message": "Nenhum script fornecido"}
    return engine.multi_pass_generation.remote(script)

@app.function(image=modal.Image.debian_slim(python_version="3.10").pip_install("fastapi"), timeout=1200)
@modal.asgi_app()
def apollo_api():
    return web_app
