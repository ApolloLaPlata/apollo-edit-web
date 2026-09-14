import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the broken assignment
    content = re.sub(r'preview\.innerHTML =\s*<div style="padding: 20px;">', 'preview.innerHTML = \\n<div style="padding: 20px;">', content)
    
    # Replace the broken closing
    content = re.sub(r'</div>\s*;', '</div>\\n;', content)
    
    # Remove the duplicated garbage block
    garbage_pattern = r'\}">\s*<h2 style="color: white; margin-bottom: 20px; text-align: center;">.*?</div>\s*;'
    content = re.sub(garbage_pattern, '}', content, flags=re.DOTALL)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {fpath}")

