import modal
import os
import shutil

apollo_image = modal.Image.debian_slim(python_version="3.10").pip_install("huggingface_hub")
apollo_volume = modal.Volume.from_name("apollo-models", create_if_missing=True)

app = modal.App("apollo-fix-volume")

@app.function(image=apollo_image, volumes={"/models": apollo_volume}, timeout=3600)
def fix_volume():
    from huggingface_hub import snapshot_download
    
    old_path = "/models/huggingface/hub/models--Lightricks--LTX-2.3"
    if os.path.exists(old_path):
        print(f"Limpando modelo antigo de 44GB: {old_path}")
        shutil.rmtree(old_path)
    
    new_repo = "CalamitousFelicitousness/LTX-2.3-Sulphur2-Base-Diffusers"
    new_path = "/models/huggingface/hub/models--CalamitousFelicitousness--LTX-2.3-Sulphur2-Base-Diffusers"
    
    print(f"Baixando versão Diffusers do LTX 2.3 (sharded)...")
    snapshot_download(repo_id=new_repo, local_dir=new_path, max_workers=8)
    
    apollo_volume.commit()
    print("Sucesso! Volume atualizado com o modelo em formato Diffusers Nativo.")

if __name__ == "__main__":
    with app.run():
        fix_volume.remote()
