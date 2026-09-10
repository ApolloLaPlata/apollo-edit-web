
import modal
app = modal.App("patcher")
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(image=universal_comfy_image, volumes={"/comfyui_models": comfy_volume})
def fix_pulid():
    import os, re
    print("Iniciando Runtime Patch do PuLID no Container...")
    hook_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/PulidFluxHook.py"
    if os.path.exists(hook_path):
        c = open(hook_path, "r").read()
        c = c.replace("def pulid_forward(self,", "def pulid_forward_orig(self,")
        c = c.replace("out = self.forward(img", "out = self.forward_orig(img")
        c = c.replace("def pulid_forward_orig(self, *args, **kwargs):", "def pulid_forward_orig(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None, **kwargs):")
        c = re.sub(r"def pulid_forward_orig\(self, img: Tensor, img_ids: Tensor, txt: Tensor, txt_ids: Tensor, timesteps: Tensor, y: Tensor, guidance: Tensor = None, control = None, transformer_options=\{\}, attn_mask: Tensor = None, \*\*kwargs\) -> Tensor:", "def pulid_forward_orig(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None, **kwargs):", c)
        open(hook_path, "w").write(c)
        print("Hook patched!")

    main_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py"
    if os.path.exists(main_path):
        c2 = open(main_path, "r").read()
        c2 = c2.replace("m.forward = pulid_forward.__get__(m, type(m))", "m.forward_orig = pulid_forward_orig.__get__(m, type(m))")
        open(main_path, "w").write(c2)
        print("Main patched!")

@app.local_entrypoint()
def main():
    fix_pulid.remote()

