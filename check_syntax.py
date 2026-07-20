import os
import py_compile
import sys

backend_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend"
errors = []

for root, _, files in os.walk(backend_dir):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                py_compile.compile(filepath, doraise=True)
            except Exception as e:
                errors.append((filepath, str(e)))

if errors:
    print(f"Encontrados {len(errors)} erros de sintaxe:")
    for filepath, err in errors:
        print(f"\n--- {filepath} ---")
        print(err)
    sys.exit(1)
else:
    print("Nenhum erro de sintaxe encontrado em toda a pasta backend/!")
