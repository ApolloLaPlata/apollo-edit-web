import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1) Fix missing opening backtick using regex to handle whitespace
    pattern1 = re.compile(r'preview\.innerHTML =\s*<div style="padding: 20px;">')
    content = re.sub(pattern1, 'preview.innerHTML = \n                    <div style="padding: 20px;">', content)
                              
    # 2) Fix missing closing backtick
    pattern2 = re.compile(r'</div>\s*;')
    content = re.sub(pattern2, '</div>\n                ;', content)
    
    # Also there was a stray block right after that in my previous output:
    # }">
    #                 <h2 style="color: white; margin-bottom: 20px; text-align: center;">🚀 Resultados da Sessão</h2>
    pattern3 = re.compile(r'\}">\s*<h2 style="color: white; margin-bottom: 20px; text-align: center;">.*?</div>\s*;', re.DOTALL)
    content = re.sub(pattern3, '}', content)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Patched {fpath}")

