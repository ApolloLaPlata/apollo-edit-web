import modal
app = modal.App("check-comfyui")

@app.function(image=modal.Image.debian_slim().apt_install("git").run_commands("git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui"))
def check_code():
    with open("/comfyui/main.py", "r") as f:
        content = f.read()
    import re
    m = re.search(r"def start_comfyui\(.*?(?=def |class )", content, re.DOTALL)
    if m:
        print("--- start_comfyui ---")
        print(m.group(0))

