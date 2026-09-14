import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix closing
    content = content.replace('</div>\n`;\n            }', '</div>\n                `;\n            }')
    content = content.replace('</div>\n                ;\n            }', '</div>\n                `;\n            }')
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {fpath}")
