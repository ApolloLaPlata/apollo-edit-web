import modal
import os
import sys

from backend.cloud_tools.engines.universal_engine import universal_comfy_image
from backend.cloud_tools.modal_app import app
from contextlib import contextmanager

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
arena_comfy_image = universal_comfy_image

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
    image=arena_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    scaledown_window=60,
    timeout=1800,
    max_containers=2,
    enable_memory_snapshot=True
)
class ArenaComfyEngine:
    FORCE_REBUILD = 1 

    @modal.enter()
    def load_model(self):
        import subprocess
        import urllib.request
                # [INJETADO V3: SUPER PATCH PARA O PULID FLUX]
        import os
        hook_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/PulidFluxHook.py"
        if os.path.exists(hook_path):
            c = open(hook_path, "r").read()
            import re
            c = re.sub(r"def pulid_forward[^\(]*\([\s\S]*?\)\s*->\s*Tensor:", "def pulid_forward(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None, **kwargs):", c)
            open(hook_path, "w").write(c)
            
        main_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py"
        if os.path.exists(main_path):
            c2 = open(main_path, "r").read()
            import re
            c2 = re.sub(r"m\.forward(?:_orig)?\s*=\s*pulid_forward(?:_orig)?\.__get__\(m, type\(m\)\)", "m.forward_orig = pulid_forward.__get__(m, type(m))", c2)
            c2 = c2.replace("from .PulidFluxHook import pulid_forward_orig", "from .PulidFluxHook import pulid_forward")
            open(main_path, "w").write(c2)
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
        )
        with open("/comfyui/extra_model_paths.yaml", "w") as f:
            f.write(yaml_content)

        self.comfy_process = None

    def _ensure_comfyui_running(self):
        import urllib.request
        import os
        import re

        # [INJETADO V4: SUPER PATCH PARA O PULID FLUX]
        pulid_dir = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll"
        if os.path.exists(pulid_dir):
            print("[ArenaComfyEngine] Downloading fresh PuLID files to undo build-time corruption...")
            try:
                urllib.request.urlretrieve("https://raw.githubusercontent.com/lldacing/ComfyUI_PuLID_Flux_ll/main/pulidflux.py", f"{pulid_dir}/pulidflux.py")
                urllib.request.urlretrieve("https://raw.githubusercontent.com/lldacing/ComfyUI_PuLID_Flux_ll/main/PulidFluxHook.py", f"{pulid_dir}/PulidFluxHook.py")
            except Exception as e:
                print(f"[ArenaComfyEngine] Failed to download fresh PuLID files: {e}")
            
            hook_path = f"{pulid_dir}/PulidFluxHook.py"
            if os.path.exists(hook_path):
                c = open(hook_path, "r").read()
                # Add **kwargs to pulid_forward_orig safely
                c = c.replace("attn_mask: Tensor = None,", "attn_mask: Tensor = None, **kwargs,")
                open(hook_path, "w").write(c)
                print("[ArenaComfyEngine] Successfully applied **kwargs patch to PulidFluxHook.py")
        import subprocess
        import time
        import sys
        
        if self.comfy_process is not None:
            return
            
        print("[ArenaComfyEngine] Patching comfy-kitchen to disable na3d and sage_attention...")
        
        print("[ArenaComfyEngine] Patching PyTorch infer_schema to use eval_str=True for inspect.signature...")
        
        patch_script = """
import os
# Patch PyTorch infer_schema
path = '/usr/local/lib/python3.10/site-packages/torch/_library/infer_schema.py'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'inspect.signature(func)' in content:
        content = content.replace('inspect.signature(func)', 'inspect.signature(func, eval_str=True)')
    append_str = '''
import typing
import torch
try:
    SUPPORTED_PARAM_TYPES[list[int]] = "int[]"
    SUPPORTED_PARAM_TYPES[list[float]] = "float[]"
    SUPPORTED_PARAM_TYPES[list[bool]] = "bool[]"
    SUPPORTED_PARAM_TYPES[list[str]] = "str[]"
    SUPPORTED_PARAM_TYPES[list[torch.Tensor]] = "Tensor[]"
    SUPPORTED_PARAM_TYPES["float"] = "float"
    SUPPORTED_PARAM_TYPES["typing.Optional[float]"] = "float?"
    SUPPORTED_PARAM_TYPES["float | None"] = "float?"
    SUPPORTED_PARAM_TYPES["bool"] = "bool"
    SUPPORTED_PARAM_TYPES["typing.Optional[bool]"] = "bool?"
    SUPPORTED_PARAM_TYPES["bool | None"] = "bool?"
    SUPPORTED_PARAM_TYPES["str"] = "str"
    SUPPORTED_PARAM_TYPES["typing.Optional[str]"] = "str?"
    SUPPORTED_PARAM_TYPES["str | None"] = "str?"
    
    SUPPORTED_PARAM_TYPES["list[int]"] = "int[]"
    SUPPORTED_PARAM_TYPES["list[float]"] = "float[]"
    SUPPORTED_PARAM_TYPES["list[bool]"] = "bool[]"
    SUPPORTED_PARAM_TYPES["list[str]"] = "str[]"
    SUPPORTED_PARAM_TYPES["list[torch.Tensor]"] = "Tensor[]"
    SUPPORTED_PARAM_TYPES["typing.List[int]"] = "int[]"
    SUPPORTED_PARAM_TYPES["typing.List[float]"] = "float[]"
    SUPPORTED_PARAM_TYPES["typing.List[bool]"] = "bool[]"
    SUPPORTED_PARAM_TYPES["typing.List[str]"] = "str[]"
    SUPPORTED_PARAM_TYPES["typing.List[torch.Tensor]"] = "Tensor[]"
    SUPPORTED_PARAM_TYPES["torch.Tensor"] = "Tensor"
    SUPPORTED_PARAM_TYPES["typing.Optional[torch.Tensor]"] = "Tensor?"
    SUPPORTED_PARAM_TYPES["torch.Tensor | None"] = "Tensor?"
    
    SUPPORTED_RETURN_TYPES["torch.Tensor"] = "Tensor"
    SUPPORTED_RETURN_TYPES["list[torch.Tensor]"] = "Tensor[]"
    SUPPORTED_RETURN_TYPES["typing.List[torch.Tensor]"] = "Tensor[]"
    SUPPORTED_RETURN_TYPES["tuple[torch.Tensor, torch.Tensor]"] = "Tensor, Tensor"
    SUPPORTED_RETURN_TYPES["tuple[torch.Tensor]"] = "Tensor"
    SUPPORTED_RETURN_TYPES["tuple[torch.Tensor, ...]"] = "Tensor[]"
except Exception:
    pass
'''
    changed = False
    if 'SUPPORTED_PARAM_TYPES["float | None"]' not in content:
        content += append_str
        changed = True
        
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# Patch comfy/ops.py para remover enable_gqa (incompativel com PyTorch 2.4.0)
ops_path = '/comfyui/comfy/ops.py'
if os.path.exists(ops_path):
    with open(ops_path, 'r', encoding='utf-8') as f:
        ops_content = f.read()
    if 'kwargs.pop("enable_gqa", None)' not in ops_content:
        import re
        ops_content = re.sub(
            r'([ \\t]*)return torch\.nn\.functional\.scaled_dot_product_attention\\(q, k, v, \\*args, \\*\\*kwargs\\)',
            r'\\1kwargs.pop("enable_gqa", None)\\n\\1return torch.nn.functional.scaled_dot_product_attention(q, k, v, *args, **kwargs)',
            ops_content
        )
        with open(ops_path, 'w', encoding='utf-8') as f:
            f.write(ops_content)
"""
        subprocess.run(["python", "-c", patch_script], check=True)
        
        # FIX Hunyuan: Install ComfyUI-HunyuanVideoWrapper
        if not os.path.exists("/comfyui/custom_nodes/ComfyUI-HunyuanVideoWrapper"):
            subprocess.run(["git", "clone", "https://github.com/kijai/ComfyUI-HunyuanVideoWrapper.git", "/comfyui/custom_nodes/ComfyUI-HunyuanVideoWrapper"])
            subprocess.run(["pip", "install", "-r", "/comfyui/custom_nodes/ComfyUI-HunyuanVideoWrapper/requirements.txt"])
            
        if not os.path.exists("/comfyui/custom_nodes/ComfyUI-OmniGen"):
            subprocess.run(["git", "clone", "https://github.com/1038lab/ComfyUI-OmniGen.git", "/comfyui/custom_nodes/ComfyUI-OmniGen"])
            subprocess.run(["pip", "install", "-r", "/comfyui/custom_nodes/ComfyUI-OmniGen/requirements.txt"])
            
        subprocess.run(["pip", "install", "transformers==4.45.2", "accelerate==0.34.2", "hf_transfer"])
        
        # PATCH transformers bug (NameError: nn)
        accelerate_path = "/usr/local/lib/python3.10/site-packages/transformers/integrations/accelerate.py"
        if os.path.exists(accelerate_path):
            with open(accelerate_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "# ANTIGRAVITY PATCH V2" not in content:
                content = "import torch\nimport torch.nn as nn\n# ANTIGRAVITY PATCH V2\n" + content
                with open(accelerate_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print("[ArenaComfyEngine] Patch do transformers (torch, nn) aplicado!")
            
        # PATCH the hardcoded private repo in the node ALWAYS
        node_file = "/comfyui/custom_nodes/ComfyUI-OmniGen/AILab_OmniGen.py"
        if os.path.exists(node_file):
            with open(node_file, "r", encoding="utf-8") as f:
                content = f.read()
            if "silveroxides" in content:
                content = content.replace("silveroxides/OmniGen-V1", "shitao/OmniGen-v1")
                content = content.replace("silveroxides", "shitao")
                with open(node_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print("[ArenaComfyEngine] Patch do repositorio OmniGen aplicado!")
        
        # Criar extra_model_paths.yaml para garantir que o ComfyUI ache os modelos no volume /comfyui_models
        yaml_content = """
comfyui_mcp:
  base_path: /comfyui_models
  checkpoints: checkpoints
  clip: clip
  clip_vision: clip_vision
  style_models: style_models
  upscale_models: upscale_models
  unet: unet
  vae: vae
  loras: loras
  controlnet: controlnet
  OmniGen: OmniGen
apollo:
  base_path: /apollo_volume/models
  unet: diffusion_models
  clip: text_encoders
  vae: vae
  upscale_models: upscale_models
"""
        with open("/comfyui/extra_model_paths.yaml", "w") as f:
            f.write(yaml_content)

        # --- SYMLINK FOR PULID ---
        try:
            os.makedirs("/comfyui/models", exist_ok=True)
            if not os.path.exists("/comfyui/models/pulid"):
                os.symlink("/comfyui_models/pulid", "/comfyui/models/pulid")
        except Exception as e:
            print("Symlink error:", e)
        # -------------------------

        print("[ArenaComfyEngine] Lancando ComfyUI como subprocesso...")
        
        # --- PATCH PULID ---
        pulid_file = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py"
        try:
            if os.path.exists(pulid_file):
                with open(pulid_file, "r") as pf:
                    pcode = pf.read()
                bad_str = "try:\n        __import__('os').makedirs(dir_path, exist_ok=True)\n    except Exception:\n        pass"
                good_str = "try:\n            __import__('os').makedirs(dir_path, exist_ok=True)\n        except Exception:\n            pass"
                if bad_str in pcode:
                    pcode = pcode.replace(bad_str, good_str)
                    with open(pulid_file, "w") as pf:
                        pf.write(pcode)
                    print("[ArenaComfyEngine] PuLID Flux node patched successfully!")
        except Exception as e:
            print(f"[ArenaComfyEngine] Failed to patch PuLID: {e}")
        # -------------------

        self.comfy_process = subprocess.Popen(
            ["comfy", "--workspace", "/comfyui", "launch", "--",
             "--listen", "127.0.0.1", "--port", "8188", "--highvram", "--extra-model-paths-config", "/comfyui/extra_model_paths.yaml", "--use-split-cross-attention"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )

        server_up = False
        start_time = time.time()
        while time.time() - start_time < 180:
            try:
                urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=1)
                print("[ArenaComfyEngine] ComfyUI is UP and Ready!")
                server_up = True
                break
            except Exception:
                time.sleep(1)
                
        if not server_up:
            print("Timeout waiting for ComfyUI to start")

    @modal.method()
    def generate(self, workflow_json: dict, source_image_b64: str = None, source_image_name: str = "referencia.jpg", multiple_images: dict = None):
        import urllib.request
                # [INJETADO V3: SUPER PATCH PARA O PULID FLUX]
        import os
        hook_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/PulidFluxHook.py"
        if os.path.exists(hook_path):
            c = open(hook_path, "r").read()
            import re
            c = re.sub(r"def pulid_forward[^\(]*\([\s\S]*?\)\s*->\s*Tensor:", "def pulid_forward(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None, **kwargs):", c)
            open(hook_path, "w").write(c)
            
        main_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py"
        if os.path.exists(main_path):
            c2 = open(main_path, "r").read()
            import re
            c2 = re.sub(r"m\.forward(?:_orig)?\s*=\s*pulid_forward(?:_orig)?\.__get__\(m, type\(m\)\)", "m.forward_orig = pulid_forward.__get__(m, type(m))", c2)
            c2 = c2.replace("from .PulidFluxHook import pulid_forward_orig", "from .PulidFluxHook import pulid_forward")
            open(main_path, "w").write(c2)
        import urllib.parse
        import json
        import time
        import base64
        import uuid
        import os

        self._ensure_comfyui_running()

        print("[ArenaComfyEngine] Recebendo workflow JSON para gerar imagem...")
        
        # Salva a imagem de referencia no input do ComfyUI se fornecida
        if source_image_b64:
            print(f"[ArenaComfyEngine] Salvando imagem de referencia: {source_image_name}")
            os.makedirs("/comfyui/input", exist_ok=True)
            with open(f"/comfyui/input/{source_image_name}", "wb") as f:
                f.write(base64.b64decode(source_image_b64))
                
        # Salva múltiplas imagens se fornecidas
        if multiple_images:
            os.makedirs("/comfyui/input", exist_ok=True)
            for img_name, img_b64 in multiple_images.items():
                print(f"[ArenaComfyEngine] Salvando imagem: {img_name}")
                with open(f"/comfyui/input/{img_name}", "wb") as f:
                    f.write(base64.b64decode(img_b64))
        req = urllib.request.Request(
            "http://127.0.0.1:8188/prompt",
            data=json.dumps({"prompt": workflow_json, "client_id": "arena-client"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                resp_data = json.loads(response.read())
                prompt_id = resp_data["prompt_id"]
        except Exception as e:
            return {"error": f"Falha ao enviar workflow: {str(e)}"}

        # Polling for completion
        while True:
            try:
                history_req = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
                with urllib.request.urlopen(history_req) as history_resp:
                    history = json.loads(history_resp.read())
                    if prompt_id in history:
                        outputs = history[prompt_id].get("outputs", {})
                        if not outputs:
                            time.sleep(1)
                            continue
                            
                        # Extrair o nome do arquivo gerado
                        for node_id, node_output in outputs.items():
                            if "images" in node_output:
                                filename = node_output["images"][0]["filename"]
                                
                                # Pegar o conteudo binario da imagem
                                get_img_req = urllib.request.Request(f"http://127.0.0.1:8188/view?filename={filename}")
                                with urllib.request.urlopen(get_img_req) as img_resp:
                                    img_bytes = img_resp.read()
                                    return {"status": "success", "image_b64": base64.b64encode(img_bytes).decode("utf-8")}
            except Exception as e:
                pass
            time.sleep(2)




