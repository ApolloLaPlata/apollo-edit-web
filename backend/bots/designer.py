import os
import requests
import json
import base64
import uuid
from dotenv import load_dotenv

load_dotenv()
APOLLO_MULTI_PASS_URL = "https://historiasde7dias--apollo-render-router-apollo-api.modal.run/generate/multi_pass"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "..", "frontend", "public", "uploads")
WORKFLOW_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\apollo_flux2_klein.json"

def gerar_imagem(prompt):
    print(f"[DESIGNER] Gerando arte via Apollo Flux2 Multi-Pass API para o prompt: {prompt}")
    
    if not os.path.exists(PUBLIC_DIR):
        os.makedirs(PUBLIC_DIR)
        
    try:
        # Carrega o JSON base do ComfyUI do diretório do Apollo Edit Web
        with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
            workflow_base = f.read()
            
        payload = {
            "script": {
                "workflow_json_string": workflow_base,
                "etapas": [
                    {
                        "prompt": prompt,
                        "tipo": "base_generation"
                    }
                ]
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(APOLLO_MULTI_PASS_URL, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "success" and "image_base64" in data:
            file_name = f"{uuid.uuid4().hex[:10]}.png"
            file_path = os.path.join(PUBLIC_DIR, file_name)
            
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(data["image_base64"]))
            
            print(f"[DESIGNER] [ OK ] Imagem Multi-Pass gerada e salva com sucesso!")
            return f"/uploads/{file_name}"
        else:
            print(f"[DESIGNER] [ERRO] Apollo retornou erro estrutural: {data}")
            return "https://via.placeholder.com/800x400.png?text=Erro+API+Apollo"
            
    except Exception as e:
        print(f"[DESIGNER] [ERRO] Falha ao conectar no Apollo API (Multi-Pass): {e}")
        return "https://via.placeholder.com/800x400.png?text=Falha+Na+Conexao"
