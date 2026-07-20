import os
import sys
import asyncio
import base64
import json
from pathlib import Path
import modal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.api.lightning_client import LightningClient
from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine, app

LIGHTNING_API_KEY = "sk-lit-8d641291-d92e-4469-8465-4a74d1c28a5d"
SYSTEM_PROMPT = """You are an expert AI image generation prompt engineer. 
Your task is to take a base scene and a list of characters, and construct a highly detailed, perfectly composed prompt for FLUX.1.
To prevent character distortion (where features of one character bleed into another), you MUST explicitly describe where each character is placed (left, right, center, foreground, background) and explicitly isolate their physical descriptions.
Return ONLY the final prompt in English. Do not add any introductory or concluding text."""

@app.local_entrypoint()
def orchestrate_multipass():
    print("--- 1. Orquestracao Autonoma (LLM) ---")
    client = LightningClient(api_key=LIGHTNING_API_KEY)
    
    global_prompt = "Three characters sitting at a bar drinking beer. An industrial steampunk environment."
    characters = [
        {"name": "Jinx", "details": "Jinx from Arcane, a pale young woman with extremely long, vibrant blue braided hair reaching her ankles, striking large neon pink eyes, and blue cloud tattoos on her left arm and torso. She is wearing a dark leather halter top with gold eyelets, detached matching sleeves, and purple striped loose pants with black combat boots. She has a manic, mischievous expression. She is sitting on the left."},
        {"name": "Elon Musk", "details": "Elon Musk, the billionaire CEO, wearing a casual light pink button-down shirt with the sleeves rolled up. He has short dark blonde hair, pale skin, a strong jawline, and a slight smirk. He is sitting in the center."},
        {"name": "Monkey", "details": "A highly realistic chimpanzee with detailed dark fur and expressive eyes, wearing a fitted beige safari shirt with pockets. He is sitting on the right."}
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

    print("\n--- 2. Gerando Imagem Base Direto ---")
    engine = UniversalComfyEngine()
    
    # Generate base image using the base model
    # Wait, the engine takes a workflow JSON string for generate.
    # Let's load the normal Flux workflow for the base generation
    base_wf_path = Path("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/apollo_flux2_klein.json")
    with open(base_wf_path, "r", encoding="utf-8") as f:
        workflow_base = f.read()
        
    print("Chamando engine.generate.remote() para Imagem Base...")
    result_base = engine.generate.remote(
        workflow_json_string=workflow_base,
        prompt=base_prompt,
        seed=42
    )
    
    if result_base.get("status") != "success":
        print(f"Erro ao gerar imagem base: {result_base}")
        return
        
    base_img_b64 = result_base.get("image_base64")
    print("[Motor Base] Imagem base gerada com sucesso!")
        
    print("\n--- 3. Carregando Imagens de Referencia ---")
    ref_paths = [
        r"C:\Users\v5est\Downloads\696191561_122139344121114074_799107263541253788_n.jpg",
        r"C:\Users\v5est\Downloads\2elon_musk_sorvete_txt2img.png",
        r"C:\Users\v5est\Downloads\Gemini_Generated_Image_trq27dtrq27dtrq2.png"
    ]
    ref_b64s = []
    for f in ref_paths:
        try:
            with open(f, "rb") as img_f:
                ref_b64s.append(base64.b64encode(img_f.read()).decode("utf-8"))
        except:
            ref_b64s.append(base_img_b64[:100] + "...") 
            print(f"Aviso: {f} nao encontrado, usando mock b64.")
            
    print("\n--- 4. Enviando para o Multipass Direto ---")
    
    wf_path = Path("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/10resultado_3_personagens_CHAINED_klein.json")
    with open(wf_path, "r", encoding="utf-8") as f:
        workflow_multipass = json.load(f)
        
    print("Chamando engine.generate.remote() para Multipass...")
    try:
        result_multi = engine.generate.remote(
            workflow_json_string=json.dumps(workflow_multipass),
            prompt=base_prompt,
            input_images_b64=[base_img_b64] + ref_b64s,
            regional_prompts=regional_prompts,
            seed=42
        )
        
        if result_multi.get("status") == "success":
            final_b64 = result_multi.get("image_base64")
            out_path = Path(os.path.dirname(__file__)) / "multipass_final_direto.png"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(final_b64))
            print(f"[Motor Multipass] SUCESSO! Imagem final salva em: {out_path}")
        else:
            print(f"Erro no fluxo multipass: {result_multi}")
            
    except Exception as e:
        print(f"Exceção no Multipass: {e}")

if __name__ == '__main__':
    pass
