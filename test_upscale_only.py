import urllib.request
import json
import time
import os
import io
import base64
from PIL import Image

def test_upscale():
    print("Iniciando Teste Upscale via HTTP API com Novo FLUX nativo...")
    
    # URL da API
    url = "https://historiasde7dias--apollo-render-router-apollo-api.modal.run"
    
    # 2. Ler a imagem base
    input_image_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\testes_modal_output\\elonmuskresultado_multipass_api_test - Copia.png"
    if not os.path.exists(input_image_path):
        print(f"Erro: Imagem de entrada não encontrada: {input_image_path}")
        return
        
    with open(input_image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    # 3. Ler o workflow
    wf_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\flux_upscale_ultrasharp.json"
    with open(wf_path, "r", encoding="utf-8") as wf_file:
        upscale_wf = json.load(wf_file)
        
    # Inject inputs omitted as they are handled by JSON and engine

    # 4. Criar o request (Multipass wrapper)
    payload = {
        "script": {
            "workflow_json_string": json.dumps(upscale_wf),
            "base_image_b64": image_base64,
            "etapas": [
                {
                    "name": "upscale"
                }
            ]
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    print("Enviando requisição via HTTP (pode demorar alguns minutos)...")
    try:
        with urllib.request.urlopen(req, timeout=1200) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        print(f"Status: {result.get('status')}")
        if result.get("status") == "success":
            print("Sucesso!")
            img_b64 = result.get("image_base64")
            if img_b64:
                img_data = base64.b64decode(img_b64)
                img = Image.open(io.BytesIO(img_data))
                out_path = f"E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\testes_modal_output\\resultado_flux_upscale_0.png"
                img.save(out_path)
                print(f"Imagem salva em: {out_path}")
            else:
                print("ERRO: Nenhuma imagem retornada!")
        else:
            print(f"ERRO: Falha na etapa: {result.get('message')}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_upscale()
