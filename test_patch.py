
import modal
app = modal.App("patch-test")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
from backend.cloud_tools.engines.universal_engine import universal_comfy_image

@app.function(image=universal_comfy_image, volumes={"/comfyui_models": comfy_volume})
def fix_pulid():
    import os, re
    pulid_hook = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/PulidFluxHook.py"
    if os.path.exists(pulid_hook):
        c = open(pulid_hook).read()
        print("BEFORE:")
        print(c[c.find("def pulid_forward"):c.find("-> Tensor:")+10])
        
        # Patch the signature to accept all *args and **kwargs dynamically
        # Since the original signature has "def pulid_forward(self, img: Tensor, img_ids: Tensor, txt: Tensor, txt_ids: Tensor, timesteps: Tensor, y: Tensor, guidance: Tensor = None, control = None, transformer_options={}, attn_mask: Tensor = None, **kwargs)"
        # Or something like that. We just need to know what it looks like now.
    else:
        print("Not found")

