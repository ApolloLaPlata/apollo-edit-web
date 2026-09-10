import modal

app = modal.App('apollo-fix-pulid')
comfy_volume = modal.Volume.from_name('comfyui-models-vol')

@app.function(volumes={'/comfyui': comfy_volume})
def fix_pulid():
    file_path = '/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py'
    with open(file_path, 'r') as f:
        content = f.read()
    
    content = content.replace('try:\n    __import__(\'os\').makedirs', 'try:\n        pass\n    except:\n        pass\n    __import__(\'os\').makedirs')
    
    with open(file_path, 'w') as f:
        f.write(content)
    comfy_volume.commit()
    print('PuLID fixed!')

@app.local_entrypoint()
def main():
    fix_pulid.remote()

