import modal
app = modal.App("debug-app")

@app.function()
def dump_file():
    with open("/root/backend/cloud_tools/engines/flux_txt2img_engine.py", "r") as f:
        print(f.read())

