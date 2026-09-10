import os
import glob

directory = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\*.py'
for filepath in glob.glob(directory):
    try:
        # Tentar ler como cp1252
        with open(filepath, 'r', encoding='cp1252') as f:
            content = f.read()
            
        # Tentar ler como utf-8 para ver se já é utf-8
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                utf8_content = f.read()
            # se não deu erro, já é utf-8!
        except UnicodeDecodeError:
            # Se deu erro, então era cp1252 (ou parecido) e precisa converter!
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Convertido: {filepath}")
    except Exception as e:
        print(f"Erro no arquivo {filepath}: {e}")
