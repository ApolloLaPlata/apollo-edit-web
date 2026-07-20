import os
import importlib
import sys
import traceback

backend_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend"
errors = []

for root, _, files in os.walk(backend_dir):
    for file in files:
        if file.endswith(".py") and not file.startswith("__"):
            filepath = os.path.join(root, file)
            # Convert filepath to module name
            rel_path = os.path.relpath(filepath, r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
            module_name = rel_path.replace(os.sep, '.')[:-3]
            try:
                importlib.import_module(module_name)
            except Exception as e:
                # ignore expected warnings about environment vars if they throw
                err_str = str(e)
                errors.append((module_name, err_str))

if errors:
    print(f"Encontrados {len(errors)} erros de importação:")
    for mod, err in errors:
        print(f"[{mod}] -> {err}")
    sys.exit(1)
else:
    print("Nenhum erro de importação encontrado (todos os módulos compilam e carregam)!")
