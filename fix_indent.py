import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\main.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("app.include_router(routes_audio_lab.router)\n    app.include_router(routes_video.router)", "app.include_router(routes_audio_lab.router)\napp.include_router(routes_video.router)")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("IndentationError consertado!")
