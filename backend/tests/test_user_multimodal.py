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
MODAL_FLUX_URL = "https://descarganews--apollo-render-router-apollo-api.modal.run/generate/image"

SYSTEM_PROMPT = """You are an expert AI image generation prompt engineer. 
Your task is to take a base scene and a list of characters, and construct a highly detailed, perfectly composed prompt for FLUX.1.
FLUX is a T5-based model, meaning it perfectly understands spatial relationships and natural language.
To prevent character distortion (where features of one character bleed into another), you MUST explicitly describe where each character is placed (left, right, center, foreground, background) and explicitly isolate their physical descriptions.

Return ONLY the final prompt in English. Do not add any introductory or concluding text."""

def orchestrate_multi_character_generation():
    print("--- 1. Iniciando Orquestração Lightning AI (Adição Iterativa) ---")
    client = LightningClient(api_key=LIGHTNING_API_KEY)
    
    base_scenario = "An industrial, dimly lit steampunk undercity environment, with metallic pipes in the background and a gritty atmosphere."
    characters = [
        {"name": "Blue-haired Girl (Jinx)", "details": "A young woman with vibrant blue braided hair, large striking pink eyes, and cloud tattoos on her pale skin, wearing a dark leather halter top with gold eyelets and purple striped pants. She is sitting on the left side of the scene."},
        {"name": "Elon Musk", "details": "Elon Musk wearing a casual black button-down shirt, eating a scoop of cookies and cream ice cream from a waffle cone. He is standing in the center of the scene."},
        {"name": "Crying Man", "details": "A distressed man in a textured grey suit jacket over a black shirt, intensely crying with tears streaming down his face, holding his head with both hands in despair. He is standing on the right side of the scene."}
    ]
    
    current_prompt = f"Base Scenario: {base_scenario}\nCreate an initial highly detailed, photorealistic, cinematic prompt for FLUX.1. Do not add any characters yet, just the environment."
    
    print("Gerando prompt da cena base...")
    try:
        scene_prompt = client.generate_text(
            prompt=current_prompt,
            system_prompt=SYSTEM_PROMPT,
            model="openai/gpt-4o"
        )
        print(f"\n[Cena Base]:\n{scene_prompt}\n")
    except Exception as e:
        print(f"Erro na comunicação com Lightning AI: {e}")
        return
        
    final_flux_prompt = scene_prompt
    
    for i, char in enumerate(characters):
        print(f"Adicionando Personagem {i+1}: {char['name']}...")
        iterative_prompt = f"""
Current Scene Prompt:
{final_flux_prompt}

Now, integrate the following new character into this scene naturally, WITHOUT altering the fundamental lighting or environment, and WITHOUT blending this character's features with any existing characters. Ensure strict spatial isolation.
New Character: {char['name']}
Description: {char['details']}

Rewrite the full prompt to include this new character seamlessly in their specified position.
        """
        try:
            final_flux_prompt = client.generate_text(
                prompt=iterative_prompt,
                system_prompt=SYSTEM_PROMPT,
                model="openai/gpt-4o"
            )
            print(f"\n[Prompt com Personagem {i+1}]:\n{final_flux_prompt}\n")
        except Exception as e:
            print(f"Erro ao adicionar personagem {char['name']}: {e}")
            return
            
    print("--- 2. Enviando para o Modal (Flux 2 Dev) ---")
    payload = {
        "prompt": final_flux_prompt,
        "model": "flux2-universal",
        "format": "horizontal", 
        "seed": -1
    }
    
    try:
        response = requests.post(MODAL_FLUX_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("image_base64"):
                b64_data = data["image_base64"]
                img_data = base64.b64decode(b64_data)
                
                output_path = Path(os.path.dirname(__file__)) / "flux_user_test.jpg"
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print(f"[OK] Imagem salva com sucesso em: {output_path}")
            else:
                print(f"Erro no payload da resposta: {data}")
        else:
            print(f"Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
         print(f"Erro na requisição para o Modal: {e}")

if __name__ == "__main__":
    orchestrate_multi_character_generation()
