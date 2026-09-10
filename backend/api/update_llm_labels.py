import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_prompt = '4. If it is MULTIPLE characters (a cast): Clearly separate their descriptions based on the Vision AI. Assign each their specific action in the scene. Add: "DISTINCT CHARACTERS, SEPARATE INDIVIDUALS, DO NOT MERGE FEATURES". Ensure each character appears only once in their respective role.'

new_prompt = '4. If it is MULTIPLE characters (a cast): Clearly separate their descriptions. Notice that the grid has visual labels (Image 1, Image 2, etc.). Explicitly use these identifiers in your description to assign each specific character their action in the scene. Add: "DISTINCT CHARACTERS, SEPARATE INDIVIDUALS, DO NOT MERGE FEATURES".'

content = content.replace(old_prompt, new_prompt)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("LLM prompt rules updated for Image labels")
