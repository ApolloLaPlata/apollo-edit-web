import sys

with open('servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_block = '''        payload = {
            "model": model_map.get(engine, engine),
            "prompt": prompt,
            "duration": float(duration)
        }'''

new_block = '''        lyrics = body.get("lyrics", "")
        payload = {
            "model": model_map.get(engine, engine),
            "prompt": prompt,
            "lyrics": lyrics,
            "duration": float(duration)
        }'''

if old_block in code:
    code = code.replace(old_block, new_block)
    with open('servidor_web.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("servidor_web.py patched successfully!")
else:
    print("Could not find block in servidor_web.py")
