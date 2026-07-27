import re

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # Replace ["comfy", ..., "--highvram"] with ["comfy", ..., "--highvram", "--disable-xformers"] if not already present
    if '"--disable-xformers"' not in content:
        content = content.replace(
            '"--highvram"]',
            '"--highvram", "--disable-xformers"]'
        )

    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(content)
    print(f"Added --disable-xformers to {f}!")
