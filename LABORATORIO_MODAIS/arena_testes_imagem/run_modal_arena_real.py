import modal
import os
import io

app = modal.App("apollo-arena-real-test")

# Imagem Docker com diffusers
arena_image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch", 
        "torchvision", 
        "diffusers", 
        "transformers", 
        "accelerate", 
        "sentencepiece",
        "protobuf"
    )
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol")

@app.function(
    image=arena_image,
    volumes={"/comfyui_models": comfy_volume},
    gpu="a100", 
    timeout=600
)
def run_hunyuan_test(prompt, ref_image_bytes):
    import torch
    from diffusers import DiffusionPipeline
    from PIL import Image
    
    print("[MODAL GPU A100] -> Iniciando Hunyuan 3.0")
    
    model_path = "/comfyui_models/checkpoints/HunyuanImage-3"
    
    try:
        pipe = DiffusionPipeline.from_pretrained(
            model_path, 
            torch_dtype=torch.float16, 
            use_safetensors=True
        ).to("cuda")
        
        print("[MODAL GPU A100] -> Modelo carregado. Gerando inferência...")
        image = pipe(
            prompt,
            num_inference_steps=25,
            guidance_scale=7.5
        ).images[0]
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()
        
    except Exception as e:
        print(f"[MODAL ERROR] Erro na execucao do modelo: {e}")
        return None

@app.local_entrypoint()
def main():
    prompt = "A highly muscular man with a thick full black beard, wearing a black beanie and a black tank top with a punisher skull logo, riding a mountain bike on a sunny beach boardwalk."
    
    ref_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\arena_testes_imagem\referencia_bombadao.jpg"
    with open(ref_path, "rb") as f:
        ref_bytes = f.read()
        
    print("Enviando dados para a Nuvem A100...")
    result_bytes = run_hunyuan_test.remote(prompt, ref_bytes)
    
    if result_bytes:
        out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\arena_testes_imagem\resultado_REAL_hunyuan.jpg"
        with open(out_path, "wb") as f:
            f.write(result_bytes)
        print(f"Sucesso! Imagem real salva em {out_path}")
    else:
        print("Falha na geracao. Verifique os logs da Modal.")
