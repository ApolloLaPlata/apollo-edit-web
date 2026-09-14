import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the fetch URLs
    content = content.replace('"http://163.176.135.59/api/', '"/api/')
    
    # Replace the file url prepend
    content = content.replace("result.file_url.startsWith('http') ? result.file_url : http://163.176.135.59;", 
                              "result.file_url.startsWith('http') ? result.file_url : ${result.file_url};")
                              
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {fpath}")

