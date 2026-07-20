import re
for filename in ['aba_configuracoes.py', 'aba_criador_templates.py']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip style='...' or style="..." arguments
    content = re.sub(r',\s*style=[\'"].*?[\'"]', '', content)
    # Also handle standalone configure(style=...)
    content = re.sub(r'\.configure\(style=[\'"].*?[\'"]\)', '.configure()', content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
print("done")
