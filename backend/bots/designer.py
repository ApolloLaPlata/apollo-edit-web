import os
import requests
import json
import base64
import uuid
from dotenv import load_dotenv

load_dotenv()
APOLLO_MODAL_URL = "https://historiasde7dias--apollo-render-router-apollo-api.modal.run/generate/image"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "..", "frontend", "public", "uploads")

def gerar_imagem(prompt, image_format="Horizontal", upscale=False):
    print(f"[DESIGNER] Gerando arte via Modal API Serverless | Formato: {image_format} | Upscale: {upscale}")
    
    if not os.path.exists(PUBLIC_DIR):
        os.makedirs(PUBLIC_DIR)
        
    try:
        import random
        # Envia os parmetros exatos esperados pelo ImageRequest (apollo_modal_engine.py)
        payload = {
            "prompt": prompt,
            "model": "flux2-universal",
            "format": image_format,
            "seed": random.randint(1, 99999999),
            "use_upscale": upscale
        }
        
        headers = {'Content-Type': 'application/json'}
        
        # Timeout longo pois Upscale leva ~36s e Cold Start pode levar mais de 60s
        response = requests.post(APOLLO_MODAL_URL, json=payload, headers=headers, timeout=120)
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
