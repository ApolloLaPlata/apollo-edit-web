import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Grab the batch generator
match = re.search(r'(@app\.post\("/api/music/generate_batch_ideas"\).*?return \{"success": False, "error": str\(e\)\}\n)', code, re.DOTALL)
if match:
    batch_code = match.group(1)
    code = code.replace(batch_code, "")
    
    # insert after auto_tag_lyrics
    code = code.replace('@app.post("/api/music/auto_tag_lyrics")', batch_code + '\n@app.post("/api/music/auto_tag_lyrics")')
    
    with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Fixed batch ideas route position.")
else:
    print("Could not find batch generator.")
