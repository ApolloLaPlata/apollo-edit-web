import os
import ast

folder = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore"
files = [f for f in os.listdir(folder) if f.startswith("aba_") and f.endswith(".py")]

for f in files:
    path = os.path.join(folder, f)
    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
        lines = len(content.split('\n'))
        print(f"{f}: {lines} lines")
