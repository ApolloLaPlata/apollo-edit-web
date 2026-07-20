import modal
import base64
import json
import os

from backend.cloud_tools.engines.universal_engine import app, UniversalComfyEngine

def get_b64(filepath):
    with open(filepath, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@app.local_entrypoint()
def main():
    print("Lendo imagem de teste e workflow...")
    with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/image_flux2/image_flux2_pulid_redux.json", "r", encoding="utf-8") as f:
        workflow_json_string = f.read()

    image_paths = [
        r"C:\Users\v5est\Downloads\Gemini_Generated_Image_tp9jhtp9jhtp9jht.png",
        r"C:\Users\v5est\Downloads\character_turnaround_1777217432020.png"
    ]
    images_array = [get_b64(path) for path in image_paths]

    print("Conectando ao Universal Engine na nuvem (Modal)...")
    engine = UniversalComfyEngine()

    print("Enviando requisicao com array de 2 imagens...")
    prompt_text = "cinematic photo, a man and a woman standing together, looking at the camera, highly detailed, realistic"

    result = engine.generate.remote(
        workflow_json_string=workflow_json_string,
        prompt=prompt_text,
        input_images_b64=images_array
    )

    if result["status"] == "success":
        output_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/testes_modal_output/jinx_pulid_multi_result.png"
        img_data = base64.b64decode(result["image_base64"])
        with open(output_path, "wb") as f:
            f.write(img_data)
        print(f"SUCESSO! Imagem salva em: {output_path}")
        print(f"Tempo de render: {result['render_time_seconds']}s")
    else:
        print("ERRO:", result.get("message"))
        print("TRACEBACK:", result.get("traceback"))

