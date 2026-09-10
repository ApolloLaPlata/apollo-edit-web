import base64
import io
import math
import os
import json
from PIL import Image, ImageDraw

def run_test():
    img_paths = [
        r"C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\.user_uploaded\media_1788820369071.jpg",
        r"C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\.user_uploaded\media_1788820454970.png"
    ]
    
    pil_imgs = []
    for p in img_paths:
        try:
            pil_imgs.append(Image.open(p).convert("RGB"))
        except Exception as e:
            print(f"Erro ao abrir {p}: {e}")
            return
            
    num_imgs = len(pil_imgs)
    cols = math.ceil(math.sqrt(num_imgs))
    rows = math.ceil(num_imgs / cols)
    
    w, h = 512, 512
    grid = Image.new("RGB", size=(cols * w, rows * h), color=(255, 255, 255))
    for i, img in enumerate(pil_imgs):
        img.thumbnail((w, h), Image.Resampling.LANCZOS)
        img_smart = Image.new("RGB", (w, h), (255, 255, 255))
        offset_x = (w - img.width) // 2
        offset_y = (h - img.height) // 2
        img_smart.paste(img, (offset_x, offset_y))
        
        draw = ImageDraw.Draw(img_smart)
        label = f"Image {i+1}"
        draw.rectangle([(10, 10), (100, 35)], fill=(0,0,0))
        draw.text((20, 15), label, fill=(255,255,255))
        
        grid.paste(img_smart, box=(i % cols * w, i // cols * h))
        
    buf = io.BytesIO()
    grid.save(buf, format="JPEG", quality=85)
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    
    print("--- 1. IMAGEM GRID GERADA COM AS LABELS ---")
    
    print("\n--- 2. CHAMANDO FLORENCE-2 NA MODAL ---")
    try:
        import modal
        engine = modal.Cls.lookup("apollo-vision-engine", "FlorenceVisionEngine")
        vision_desc = engine().analyze_image.remote("data:image/jpeg;base64," + b64_str)
        print("RESPOSTA DO FLORENCE-2:")
        print(vision_desc)
    except Exception as e:
        print(f"Erro na Modal/Florence: {e}")
        return

    print("\n--- 3. CHAMANDO LLM (NEMOTRON) ---")
    try:
        import requests
        admin_cfg = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\admin_config.json"
        with open(admin_cfg, 'r', encoding='utf-8') as f:
            c = json.load(f)
            keys = c.get("api_config", {}).get("api_keys", [])
            lit_key = keys[0] if keys else ""
            
        user_prompt = "A mulher da Image 1 sentada na mesa tomando cafe com a mulher da Image 2."
        llm_prompt = '''You are an expert AI prompt engineer for Qwen 2.5 Image Edit.
    The user provided a reference image (which may be a single character's turnaround sheet, OR a grid compilation of multiple different characters) and a raw prompt: "''' + user_prompt + '''"
    
    Our Vision AI analyzed this reference image and described it as:
    "''' + vision_desc.replace('\n', ' ') + '''"
    
    Your task is to rewrite the user's prompt into a highly detailed, descriptive prompt suitable for Qwen.
  Rules for Qwen:
  1. Describe the final scene clearly, dynamically, and comprehensively in English. Do NOT copy the exact poses from the reference images; create the NEW scene requested by the user.
  2. Character Identification: Determine if the user is asking for ONE character or MULTIPLE different characters.
  3. If it is ONE character: Apply "Semantic Shielding" to prevent cloning. Add: "SINGLE CHARACTER ONLY, NO CLONES, DO NOT REPEAT".
  4. If it is MULTIPLE characters (a cast): Clearly separate their descriptions. Notice that the grid has visual labels (Image 1, Image 2, etc.). Explicitly use these identifiers in your description to assign each specific character their action in the scene. Add: "DISTINCT CHARACTERS, SEPARATE INDIVIDUALS, DO NOT MERGE FEATURES".
  5. NEW RULE: Generate an intelligent "negative_prompt" to exclude things the user DOES NOT want, based on the requested style.
  6. Output ONLY a valid JSON array with exactly ONE object. Format: [{"prompt": "...", "negative_prompt": "...", "image_indices": [0]}]
  '''
        
        headers = {"Authorization": f"Bearer " + lit_key, "Content-Type": "application/json"}
        url_nv = "https://api.groq.com/openai/v1/chat/completions"
        if "openrouter" in lit_key or lit_key.startswith("sk-or"):
            url_nv = "https://openrouter.ai/api/v1/chat/completions"
            
        payload = {
            "model": "nvidia/llama-3.1-nemotron-70b-instruct" if "openrouter" in url_nv else "llama3-70b-8192",
            "messages": [{"role": "user", "content": llm_prompt}],
            "temperature": 0.7
        }
        r = requests.post(url_nv, headers=headers, json=payload)
        
        print("RESPOSTA DO LLM:")
        print(r.json())
        
    except Exception as e:
        print(f"Erro no LLM: {e}")

if __name__ == "__main__":
    run_test()
