import ast
filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore\aba_mapeador_automatico.py'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# I want to save a copy to the scratch folder so I can edit it freely
dest = r'C:\Users\v5est\.gemini\antigravity\brain\9270dd65-160e-47e8-aea2-6a92fd50cfc6\scratch\mapper_raw.py'
with open(dest, 'w', encoding='utf-8') as f:
    f.write(content)
