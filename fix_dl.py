import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the download URL issue
    content = content.replace("http://163.176.135.59", "${result.file_url}")
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
