import requests
import json

def run_test():
    vision_desc = "The image is a collage of two characters. Image 1 shows a highly detailed turnaround of a woman with black hair, athletic build, wearing a blue sports bra and black leggings. Image 2 shows a woman with dark hair wearing a yellow '60 Anos Cacique' t-shirt talking on a cellphone."
    user_prompt = "A mulher da Image 1 sentada na mesa tomando cafe com a mulher da Image 2."
    
    llm_prompt = '''You are an expert AI prompt engineer for Qwen 2.5 Image Edit.
    The user provided a reference image (which may be a single character's turnaround sheet, OR a grid compilation of multiple different characters) and a raw prompt: "''' + user_prompt + '''"
    
    Our Vision AI analyzed this reference image and described it as:
    "''' + vision_desc + '''"
    
    Your task is to rewrite the user's prompt into a highly detailed, descriptive prompt suitable for Qwen.
  Rules for Qwen:
  1. Describe the final scene clearly, dynamically, and comprehensively in English. Do NOT copy the exact poses from the reference images; create the NEW scene requested by the user.
  2. Character Identification: Determine if the user is asking for ONE character or MULTIPLE different characters.
  3. If it is ONE character: Apply "Semantic Shielding" to prevent cloning. Add: "SINGLE CHARACTER ONLY, NO CLONES, DO NOT REPEAT".
  4. If it is MULTIPLE characters (a cast): Clearly separate their descriptions. Notice that the grid has visual labels (Image 1, Image 2, etc.). Explicitly use these identifiers in your description to assign each specific character their action in the scene. Add: "DISTINCT CHARACTERS, SEPARATE INDIVIDUALS, DO NOT MERGE FEATURES".
  5. NEW RULE: Generate an intelligent "negative_prompt" to exclude things the user DOES NOT want, based on the requested style.
  6. Output ONLY a valid JSON array with exactly ONE object. Format: [{"prompt": "...", "negative_prompt": "...", "image_indices": [0]}]
  '''
    
    admin_cfg = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\admin_config.json"
    lit_key = ""
    with open(admin_cfg, 'r', encoding='utf-8') as f:
        c = json.load(f)
        keys = c.get("api_config", {}).get("lightning_chat", {}).get("api_keys", [])
        lit_key = keys[0] if keys else ""
        
    headers = {"Authorization": f"Bearer {lit_key}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "messages": [{"role": "user", "content": llm_prompt}],
        "temperature": 0.7
    }
    
    r = requests.post("https://lightning.ai/api/v1/chat/completions", headers=headers, json=payload)
    print(r.text)

run_test()
