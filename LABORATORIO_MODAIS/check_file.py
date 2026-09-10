import modal

app = modal.App('checker')
image = modal.Image.debian_slim().add_local_python_source('backend')

@app.local_entrypoint()
def run():
    check.remote()

@app.function(image=image)
def check():
    with open('/root/backend/cloud_tools/engines/comfy_experimental.py') as f:
        print(f.read())
