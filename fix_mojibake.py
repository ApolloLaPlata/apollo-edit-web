import os
import glob

def fix_mojibake(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    
    try:
        # Tenta decodificar o UTF-8 corrompido como latin-1 e reencodar
        # Isso corrige quando caracteres utf-8 são lidos como ISO-8859-1 e depois salvos como UTF-8
        text = content.decode('utf-8')
        fixed_text = text.encode('latin-1').decode('utf-8')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
        print(f'Fixed {file_path}')
    except Exception as e:
        pass # Se falhar, nÃ£o era esse tipo de corrupÃ§Ã£o

for root, _, files in os.walk('web_ui'):
    for file in files:
        if file.endswith(('.html', '.js', '.css', '.md')):
            fix_mojibake(os.path.join(root, file))

for root, _, files in os.walk('public'):
    for file in files:
        if file.endswith(('.html', '.js', '.css', '.md')):
            fix_mojibake(os.path.join(root, file))

