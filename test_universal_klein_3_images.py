import modal
import base64
import json
import os
import sys

from backend.cloud_tools.engines.universal_engine import app, UniversalComfyEngine

def get_b64(filepath):
    print(f"Lendo {filepath}...")
    with open(filepath, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@app.local_entrypoint()
def main():
    print("Iniciando Teste de Workflow com 3 Imagens via Batch (PuLID + Redux)...")
    
    # 1. Carregar Workflow Original do PuLID que usa Batch (Fallback)
    workflow_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\FLUX.2 [KLEIN] 4B\FLUX.2 [KLEIN] 4B Edição de imagem\workflow_multipass_klein.json"
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_json_string = f.read()

    import json
    workflow = json.loads(workflow_json_string)
    
    
        
    workflow_json_string = json.dumps(workflow)

    # 2. Ler as 3 imagens do usuario
    image_paths = [
        r"C:\Users\v5est\Downloads\696191561_122139344121114074_799107263541253788_n.jpg",
        r"C:\Users\v5est\Downloads\ComfyUI_00038_.png",
        r"C:\Users\v5est\Downloads\16e663dc-9a35-41fe-8e7e-acb4f0883069.jpg"
    ]
    
    try:
        images_array = [get_b64(path) for path in image_paths]
    except Exception as e:
        print(f"Erro ao ler imagens: {e}")
        return

    
    # Criar uma imagem base cinza para a primeira iteracao
    from PIL import Image as PILImage
    import io
    base_img = PILImage.new('RGB', (1024, 1024), color=(128, 128, 128))
    buffered = io.BytesIO()
    base_img.save(buffered, format='PNG')
    import base64
    base_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Adicionar a base como primeira imagem
    images_array.insert(0, base_b64)

    print("Conectando ao Universal Engine na nuvem (Modal)...")
    engine = UniversalComfyEngine()

    print("Enviando requisicao com array de 3 imagens...")
    prompt_text = "A cinematic, ultra realistic photograph of three characters sitting side by side at a rustic bar table having drinks, facing the camera. They are perfectly spaced out, not overlapping, all looking at the camera, 8k resolution, photorealistic"
    
    regional_prompts = [
        "a young woman sitting at the left side of a rustic bar table, cinematic",
        "a middle-aged man with glasses sitting in the middle of the rustic bar table, cinematic",
        "a chimpanzee acting like an old man sitting at the right side of the rustic bar table, cinematic"
    ]

    result = engine.generate.remote(
        workflow_json_string=workflow_json_string,
        prompt=prompt_text,
        input_images_b64=images_array,
        regional_prompts=regional_prompts
    )

    if result["status"] == "success":
        output_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/testes_modal_output/resultado_3_personagens_CHAINED_klein.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img_data = base64.b64decode(result["image_base64"])
        with open(output_path, "wb") as f:
            f.write(img_data)
        print(f"SUCESSO! Imagem salva em: {output_path}")
        print(f"Tempo de render: {result['render_time_seconds']}s")
    else:
        print("ERRO:", result.get("message"))
        print("TRACEBACK:", result.get("traceback"))

if __name__ == "__main__":
    main()
