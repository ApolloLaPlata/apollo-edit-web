import modal
import base64
import json
import os
import copy
import sys

from backend.cloud_tools.engines.universal_engine import app, UniversalComfyEngine

def get_b64(filepath):
    print(f"Lendo {filepath}...")
    with open(filepath, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@app.local_entrypoint()
def main():
    print("Iniciando Teste de Workflow com 3 Imagens (Mockup)...")
    
    # 1. Carregar Workflow Original de Mockup
    workflow_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/Mockup de Produto(Flux.2 Dev FF8)/image_flux2_fp8.json"
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    print("Injetando o terceiro nÃ³ dinamicamente no JSON...")
    
    # Adicionando o 3o LoadImage
    workflow["99_APOLLO_LOAD_3"] = {
        "class_type": "LoadImage",
        "inputs": {"image": "image3.png"},
        "_meta": {"title": "Carregar Imagem 3"}
    }

    # Adicionando o 3o ImageScale
    scale_copy = copy.deepcopy(workflow["62:41"])
    scale_copy["inputs"]["image"] = ["99_APOLLO_LOAD_3", 0]
    workflow["99_APOLLO_SCALE_3"] = scale_copy

    # Adicionando o 3o VAEEncode
    vae_copy = copy.deepcopy(workflow["62:40"])
    vae_copy["inputs"]["pixels"] = ["99_APOLLO_SCALE_3", 0]
    workflow["99_APOLLO_VAE_3"] = vae_copy

    # Adicionando o 3o ReferenceLatent (Encadeado apois o 2o)
    ref_copy = copy.deepcopy(workflow["62:39"])
    ref_copy["inputs"]["latent"] = ["99_APOLLO_VAE_3", 0]
    ref_copy["inputs"]["conditioning"] = ["62:39", 0] # O Node 62:39 eh o ultimo ReferenceLatent original
    workflow["99_APOLLO_REF_3"] = ref_copy

    # Atualizando o BasicGuider para apontar para o novo ultimo ReferenceLatent
    workflow["62:22"]["inputs"]["conditioning"] = ["99_APOLLO_REF_3", 0]

    workflow_json_string = json.dumps(workflow)

    # 2. Ler as 3 imagens do usuario
    image_paths = [
        r"C:\Users\v5est\Downloads\Gemini_Generated_Image_usp6kdusp6kdusp6.png",
        r"C:\Users\v5est\Downloads\character_turnaround_1777218541611.png",
        r"C:\Users\v5est\Downloads\character_turnaround_1777218163561.png"
    ]
    
    try:
        images_array = [get_b64(path) for path in image_paths]
    except Exception as e:
        print(f"Erro ao ler imagens: {e}")
        return

    print("Conectando ao Universal Engine na nuvem (Modal)...")
    engine = UniversalComfyEngine()

    print("Enviando requisicao com array de 3 imagens...")
    prompt_text = "Lula and Janja standing side by side with a third cinematic character, detailed, ultra realistic photograph"

    result = engine.generate.remote(
        workflow_json_string=workflow_json_string,
        prompt=prompt_text,
        input_images_b64=images_array
    )

    if result["status"] == "success":
        output_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/testes_modal_output/resultado_3_personagens_mockup.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img_data = base64.b64decode(result["image_base64"])
        with open(output_path, "wb") as f:
            f.write(img_data)
        print(f"SUCESSO! Imagem salva em: {output_path}")
        print(f"Tempo de render: {result['render_time_seconds']}s")
    else:
        print("ERRO:", result.get("message"))
        print("TRACEBACK:", result.get("traceback"))
