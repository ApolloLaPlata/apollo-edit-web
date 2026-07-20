import os
import glob

directory = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui'
files = glob.glob(os.path.join(directory, 'noticias*.html')) + [os.path.join(directory, 'hub.html')]

script_tag = '<script src="copilot_hud.js"></script>'

for file in files:
    try:
        with open(file, 'r', encoding='latin-1') as f:
            content = f.read()
        
        if script_tag not in content:
            content = content.replace('</body>', f'    {script_tag}\n</body>')
            with open(file, 'w', encoding='latin-1') as f:
                f.write(content)
            print(f'Injetado em: {os.path.basename(file)}')
    except Exception as e:
        print(f'Erro em {os.path.basename(file)}: {e}')
