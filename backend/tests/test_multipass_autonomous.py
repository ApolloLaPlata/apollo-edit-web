import os
import sys
import asyncio
import base64
import requests
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.lightning_client import LightningClient

LIGHTNING_API_KEY = "sk-lit-8d641291-d92e-4469-8465-4a74d1c28a5d"
MODAL_BASE_URL = "https://descarganews--apollo-render-router-apollo-api.modal.run"

SYSTEM_PROMPT = """You are an expert AI image generation prompt engineer. 
Your task is to take a base scene and a list of characters, and construct a highly detailed, perfectly composed prompt for FLUX.1.
To prevent character distortion (where features of one character bleed into another), you MUST explicitly describe where each character is placed (left, right, center, foreground, background) and explicitly isolate their physical descriptions.
Return ONLY the final prompt in English. Do not add any introductory or concluding text."""

def orchestrate_multipass():
    print("--- 1. Orquestracao Autonoma (LLM) ---")
    client = LightningClient(api_key=LIGHTNING_API_KEY)
    
    global_prompt = "Three characters sitting at a bar drinking beer. An industrial steampunk environment."
    characters = [
        {"name": "Person 1", "details": "A man wearing a casual shirt. He is sitting on the left."},
        {"name": "Person 2", "details": "A man wearing a casual shirt. He is sitting in the center."},
        {"name": "Person 3", "details": "A man wearing a casual shirt. He is sitting on the right."}
    ]
    
    current_prompt = f"Base Scenario: {global_prompt}\nCreate an initial highly detailed, photorealistic, cinematic prompt for FLUX.1. Do not add any characters yet, just the empty environment."
    print("[LLM] Gerando prompt do cenario base...")
    base_prompt = client.generate_text(prompt=current_prompt, system_prompt=SYSTEM_PROMPT, model="openai/gpt-4o")
    print(f"\n-> Cenario Base:\n{base_prompt}\n")
    
    regional_prompts = []
    final_flux_prompt = base_prompt
    
    for i, char in enumerate(characters):
        print(f"[LLM] Adicionando Personagem {i+1}...")
        iterative_prompt = f"Current Scene Prompt:\n{final_flux_prompt}\n\nNow, integrate the following new character naturally, WITHOUT altering the fundamental lighting, and WITHOUT blending features. Ensure spatial isolation.\nNew Character: {char['name']}\nDescription: {char['details']}\nRewrite the full prompt to include this new character seamlessly."
        
        final_flux_prompt = client.generate_text(prompt=iterative_prompt, system_prompt=SYSTEM_PROMPT, model="openai/gpt-4o")
        regional_prompts.append(final_flux_prompt)
        print(f"\n-> Prompt Inpaint Iteracao {i+1}:\n{final_flux_prompt}\n")

    print("\n--- 2. Gerando Imagem Base (Text-to-Image) ---")
    payload_base = {
        "prompt": base_prompt,
        "model": "flux2-universal",
        "format": "horizontal",
        "seed": 42
    }
    
    resp_base = requests.post(f"{MODAL_BASE_URL}/generate/image", json=payload_base)
    if resp_base.status_code != 200:
        print(f"Erro ao gerar imagem base (HTTP {resp_base.status_code}): {resp_base.text}")
        return
        
    print(f"Raw response: {resp_base.text}")
    base_img_b64 = None
    for line in resp_base.iter_lines():
        if line:
            try:
                data = json.loads(line.decode('utf-8'))
                if data.get("status") == "success":
                    base_img_b64 = data.get("image_base64")
                    print("[Motor Base] Imagem base gerada com sucesso!")
                elif data.get("status") == "error":
                    print(f"Erro reportado no payload: {data}")
            except json.JSONDecodeError:
                pass
                
    if not base_img_b64:
        print("Falha ao obter image_base64 da imagem base.")
        return
        
    print("\n--- 3. Carregando Imagens de Referencia ---")
    ref_paths = [
        r"E:\Salva Aqui\DESCARGA NEWS\DESCARGA NEWS SALVA AQUI\download (25).jpg",
        r"E:\Salva Aqui\DESCARGA NEWS\DESCARGA NEWS SALVA AQUI\download (29).jpg",
        r"E:\Salva Aqui\DESCARGA NEWS\DESCARGA NEWS SALVA AQUI\download (13).jpg"
    ]
    ref_b64s = []
    for f in ref_paths:
        try:
            with open(f, "rb") as img_f:
                ref_b64s.append(base64.b64encode(img_f.read()).decode("utf-8"))
        except:
            ref_b64s.append(base_img_b64[:100] + "...") 
            print(f"Aviso: {f} nao encontrado, usando mock b64.")
            
    print("\n--- 4. Enviando para o Multipass (Inpaint Sequencial) ---")
    
    # Carregar o workflow de inpaint
    wf_path = Path("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/10resultado_3_personagens_CHAINED_klein.json")
    with open(wf_path, "r") as f:
        workflow_multipass = json.load(f)
        
    payload_multi = {
        "workflow": workflow_multipass,
        "base_prompt": base_prompt,
        "regional_prompts": regional_prompts,
        "input_images_b64": [base_img_b64] + ref_b64s,
        "seed": 42
    }
    
    print("Sending request to multipass...")
    resp_multi = requests.post(f"{MODAL_BASE_URL}/generate/multipass", json=payload_multi, stream=True, timeout=1300)
    print(f"Status Code: {resp_multi.status_code}")
    if resp_multi.status_code != 200:
        print(f"Erro no Multipass: {resp_multi.text}")
        return
    
    final_b64 = None
    for line in resp_multi.iter_lines():
        if line:
            line_str = line.decode('utf-8').strip()
            try:
                data = json.loads(line_str)
                status = data.get("status")
                if status == "success":
                    final_b64 = data.get("image_base64")
                    out_path = Path(os.path.dirname(__file__)) / "multipass_final.png"
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(final_b64))
                    print(f"\n[Motor Multipass] SUCESSO! Imagem final salva em: {out_path}")
                    break
                elif status == "error":
                    print(f"\nErro no fluxo multipass: {data}")
                    break
                elif status == "processing":
                    print(".", end="", flush=True)
                else:
                    # Resultado sem campo "status" explícito — pode ser o resultado direto
                    if data.get("image_base64"):
                        final_b64 = data.get("image_base64")
                        out_path = Path(os.path.dirname(__file__)) / "multipass_final.png"
                        with open(out_path, "wb") as f:
                            f.write(base64.b64decode(final_b64))
                        print(f"\n[Motor Multipass] SUCESSO! Imagem final salva em: {out_path}")
                        break
                    else:
                        print(f"\n[Dados recebidos]: {str(data)[:200]}")
            except json.JSONDecodeError:
                print(f"\n[Linha não-JSON]: {line_str[:200]}")
        else:
            # linha vazia = heartbeat/espaço do servidor
            print(".", end="", flush=True)
    
    if not final_b64:
        print("\n[AVISO] Pipeline concluiu mas nenhuma imagem foi retornada.")

if __name__ == '__main__':
    orchestrate_multipass()
