import re

files = [
    'backend/cloud_tools/engines/flux_txt2img_engine.py',
    'backend/cloud_tools/engines/universal_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    
    # Remove the caching block
    pattern = r'(\s+print\("\[.*?\] Caching models into RAM[\s\S]*?print\("\[.*?\] Caching finished!"\))'
    new_content, count = re.subn(pattern, '', content)
    
    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(new_content)
    print(f"Cleaned {f}! Removed {count} caching loops.")
