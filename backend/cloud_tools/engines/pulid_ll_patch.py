import re
import os

pulid_path = '/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/PulidFluxHook.py'
with open(pulid_path, 'r') as f:
    pulid = f.read()

# Patch para aceitar kwargs (como timestep_zero_index) na versao atualizada do ComfyUI
pulid = re.sub(r'(attn_mask:\s*Tensor\s*=\s*None,?)(\s*\)\s*->\s*Tensor:)', r'\1\n    **kwargs,\2', pulid)

with open(pulid_path, 'w') as f:
    f.write(pulid)
print("[PATCH] ComfyUI_PuLID_Flux_ll atualizado com **kwargs")

pulid_path_2 = '/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py'
with open(pulid_path_2, 'r') as f:
    pulid2 = f.read()

patch_code = "try:\\n        __import__('os').makedirs(dir_path, exist_ok=True)\\n    except Exception:\\n        pass"
pulid2 = re.sub(r"os\.makedirs\(dir_path(?:,\s*exist_ok=True)?\)", patch_code, pulid2)

with open(pulid_path_2, 'w') as f:
    f.write(pulid2)
print("[PATCH] ComfyUI_PuLID_Flux_ll atualizado com exist_ok=True e prevenção de FileExistsError")
