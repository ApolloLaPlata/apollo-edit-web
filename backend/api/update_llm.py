# coding: utf-8
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_llm_prompt = '''                      llm_prompt = f"""You are an expert AI prompt engineer for Qwen 2.5 Image Edit.
  The user provided a reference image (which may be a single character's turnaround sheet, OR a grid compilation of multiple different characters) and a raw prompt: \\"{req_json.get('prompt')}\\"
  
  Our Vision AI analyzed this reference image and described it as:
  "{vision_desc}"
  
  Your task is to rewrite the user's prompt into a highly detailed, descriptive prompt suitable for Qwen.
Rules for Qwen:
1. Describe the final scene clearly, dynamically, and comprehensively in English. Do NOT copy the exact poses from the reference images; create the NEW scene requested by the user.
2. Character Identification: Determine if the user is asking for ONE character or MULTIPLE different characters.
3. If it is ONE character: Apply "Semantic Shielding" to prevent cloning. Add: "SINGLE CHARACTER ONLY, NO CLONES, DO NOT REPEAT".
4. If it is MULTIPLE characters (a cast): Clearly separate their descriptions based on the Vision AI. Assign each their specific action in the scene. Add: "DISTINCT CHARACTERS, SEPARATE INDIVIDUALS, DO NOT MERGE FEATURES". Ensure each character appears only once in their respective role.
5. NEW RULE: Generate an intelligent "negative_prompt" to exclude things the user DOES NOT want, based on the requested style (e.g. if photorealistic, exclude 'anime, drawing').
6. Output ONLY a valid JSON array with exactly ONE object.
Format:
[
  {{
    "prompt": "The highly detailed rewritten prompt here...",
    "negative_prompt": "The negative prompt here...",
    "image_indices": [0]
  }}
]
Do not include markdown blocks."""'''

# Substitui o bloco antigo do llm_prompt
content = re.sub(r'llm_prompt = f\"\"\"You are an expert AI prompt engineer for Qwen 2.5 Image Edit\..*?Do not include markdown blocks\.\"\"\"', new_llm_prompt.strip(), content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("LLM Prompt atualizado com sucesso!")
