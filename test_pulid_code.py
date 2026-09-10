
import modal
import os

app = modal.App("test-pulid")
comfy_volume = modal.Volume.from_name("comfyui-models-vol")

# Use a lightweight image with git just to clone and read the file
image = modal.Image.debian_slim().apt_install("git").run_commands([
    "git clone https://github.com/lldacing/ComfyUI_PuLID_Flux_ll.git /pulid"
])

@app.function(image=image)
def read_pulid():
    file_path = "/pulid/pulidflux.py"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "forward_orig" in line or "NextDiT" in line:
                    print(f"Line {i+1}: {line.strip()}")
    else:
        print("File not found")

