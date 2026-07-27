import modal

app = modal.App()

@app.local_entrypoint()
def main():
    print("Warming up Flux2Txt2ImgEngine...")
    Flux2 = modal.Cls.from_name("apollo-render-router", "Flux2Txt2ImgEngine")
    # This will trigger the snapshot build for Flux2Txt2ImgEngine!
    Flux2().generate.spawn(prompt='Warmup', aspect_ratio='square', seed=1)
    
    print("Warming up UniversalComfyEngine...")
    Universal = modal.Cls.from_name("apollo-render-router", "UniversalComfyEngine")
    # This will trigger the snapshot build for UniversalComfyEngine!
    Universal().generate.spawn(workflow_json_string='{}')
    print("Warmup calls spawned successfully!")
