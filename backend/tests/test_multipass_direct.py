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
To prevent character distortion and DUPLICATION, you MUST explicitly describe where each character is placed (left, right, center) and explicitly isolate their physical descriptions.
CRITICAL: You must explicitly state EXACTLY how many people are in the entire scene at this stage (e.g., "There is ONLY ONE person in the scene", or "There are EXACTLY TWO people in the room: [Character A] on the left and [Character B] in the center"). NEVER describe the same character twice. If a character was already in the scene, keep their exact description but emphasize they are the SAME person as before, to prevent the AI from generating duplicates.
Return ONLY the final prompt in English. Do not add any introductory or concluding text."""

@app.local_entrypoint()
def orchestrate_multipass():
    print("--- 1. Orquestracao Autonoma (LLM) ---")
    client = LightningClient(api_key=LIGHTNING_API_KEY)
    
    global_prompt = "An empty wooden table in a dimly lit, rustic steampunk bar. High quality, photorealistic, cinematic lighting. There is NO ONE in the scene yet."
    characters = [
        {"name": "Realistic Woman with Blue Hair", "details": "A single beautiful photorealistic young human woman with vibrant long blue hair, large striking pink eyes, and blue cloud tattoos on her left arm. She is wearing a black crop top with crossed laces and maroon striped pants. Highly detailed real human face, photographic texture, realistic skin pores. She is the ONLY person sitting on the left side of the table, sitting alone on her chair."},
        {"name": "Guy with glasses", "details": "A middle-aged man with short greyish hair and a mustache, wearing rectangular glasses and a light pink button-up shirt. He is sitting in the center of the table, smiling gently."},
        {"name": "Monkey driver", "details": "A chimpanzee with a grey beard, wearing a beige short-sleeve button-up driver's shirt with a brown pocket on the chest. He is sitting on the right side of the table."}
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
        r"C:\Users\v5est\Downloads\ComfyUI_00038_.png",
        r"C:\Users\v5est\Downloads\16e663dc-9a35-41fe-8e7e-acb4f0883069.jpg"
    ]
    ref_b64s = []
    for f in ref_paths:
        try:
            with open(f, "rb") as img_f:
                ref_b64s.append(base64.b64encode(img_f.read()).decode("utf-8"))
        except:
            ref_b64s.append(base_img_b64[:100] + "...") 
            print(f"Aviso: {f} nao encontrado, usando mock b64.")
            
    print("\n--- 4. Enviando para o Multipass Direto (Inpainting Chars) ---")
    
    wf_path = Path("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/10resultado_3_personagens_CHAINED_klein.json")
    with open(wf_path, "r", encoding="utf-8") as f:
        workflow_multipass = json.load(f)
        
    script_payload = {
        "workflow_json_string": json.dumps(workflow_multipass),
        "base_image_b64": base_img_b64,
        "etapas": []
    }
    
    for i, ref_b64 in enumerate(ref_b64s):
        script_payload["etapas"].append({
            "prompt": regional_prompts[i],
            "image_b64": ref_b64
        })

    print("Chamando engine.multi_pass_generation.remote() com 3 personagens...")
    try:
        result_multi = engine.multi_pass_generation.remote(script_payload)
        
        if result_multi.get("status") == "success":
            final_image_bytes = base64.b64decode(result_multi.get("image_base64"))
            out_path = Path(os.path.dirname(__file__)) / "multipass_final_direto.png"
            with open(out_path, "wb") as f:
                f.write(final_image_bytes)
            print(f"\n[Motor Multipass] SUCESSO! Imagem inpaint salva em: {out_path}")

            print("\n--- 5. Aplicando Upscale Final (flux_upscale_ultrasharp.json) ---")
            upscale_wf_path = Path(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\flux_upscale_ultrasharp.json")
            with open(upscale_wf_path, "r", encoding="utf-8") as f:
                workflow_upscale = f.read()

            final_b64 = base64.b64encode(final_image_bytes).decode('utf-8')
            print("Chamando engine.generate.remote() para Upscale COM PROMPT...")
            try:
                upscale_result = engine.generate.remote(
                    workflow_json_string=workflow_upscale,
                    input_image_b64=final_b64,
                    prompt=regional_prompts[-1] # PASSAR O PROMPT É CRUCIAL PARA FLUX NÃO GERAR QUADRADO BRANCO!
                )
                upscale_out_path = Path(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\tests\multipass_final_upscaled.png")
                with open(upscale_out_path, "wb") as f:
                    f.write(base64.b64decode(upscale_result.get("image_base64")))
                print(f"\n[Motor Upscale] SUCESSO ABSOLUTO! Imagem final com upscale salva em: {upscale_out_path}")
            except Exception as e:
                print(f"[Erro Upscale] Ocorreu um erro no upscale: {e}")
                
        else:
            print(f"Erro no fluxo multipass: {result_multi}")
            
    except Exception as e:
        import traceback
        print(f"Exceção no Multipass: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    orchestrate_multipass()
