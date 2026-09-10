import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Adicionar o import
if 'routes_audio_lab' not in content:
    import_target = 'from backend.api import routes_video'
    import_replacement = 'from backend.api import routes_audio_lab\nfrom backend.api import routes_video'
    content = content.replace(import_target, import_replacement)

# 2. Adicionar app.include_router
if 'app.include_router(routes_audio_lab.router)' not in content:
    router_target = 'app.include_router(routes_video.router)'
    router_replacement = 'app.include_router(routes_audio_lab.router)\n    app.include_router(routes_video.router)'
    content = content.replace(router_target, router_replacement)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Registrado routes_audio_lab no main.py!")
