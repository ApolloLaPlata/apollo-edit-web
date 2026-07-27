import modal
app = modal.App("check-comfyui")

@app.function(image=modal.Image.debian_slim().apt_install("git").run_commands("git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui"))
def check_code():
    with open("/comfyui/comfy/model_management.py", "r") as f:
        content = f.read()
    import re
    m = re.search(r"def get_torch_device\(\):.*?(?=def |class )", content, re.DOTALL)
    if m:
        print("--- get_torch_device ---")
        print(m.group(0))

