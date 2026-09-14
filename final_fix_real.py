import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Let's just do a plain replace now that we know what's there
    content = content.replace('preview.innerHTML = \n<div style="padding: 20px;">', 'preview.innerHTML = `\n<div style="padding: 20px;">')
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {fpath}")
