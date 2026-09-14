import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1) Fix missing opening backtick
    content = content.replace("preview.innerHTML = \n                    <div style=\"padding: 20px;\">", 
                              "preview.innerHTML = \n                    <div style=\"padding: 20px;\">")
                              
    # 2) Fix missing closing backtick
    content = content.replace("</div>\n                ;", "</div>\n                ;")
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Patched {fpath}")

