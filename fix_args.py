import re

for filename in ['aba_dashboard.py', 'aba_mapeador_automatico.py']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r',\s*bd=\d+', '', content)
    content = re.sub(r',\s*relief=tk\.[A-Z]+', '', content)
    content = re.sub(r',\s*relief="[a-z]+"', '', content)
    content = re.sub(r',\s*relief=\'[a-z]+\'', '', content)
    content = re.sub(r',\s*borderwidth=\d+', '', content)
    content = re.sub(r',\s*highlightthickness=\d+', '', content)
    content = re.sub(r',\s*wraplength=\d+', '', content)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

print("Attributes stripped.")
