import re

with open('apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'app.mount("/media"' not in content:
    content = content.replace('app.mount("/temp", StaticFiles(directory=temp_files_dir), name="temp")', 'app.mount("/media", StaticFiles(directory="/home/ubuntu/apollo_edit/media"), name="media")\napp.mount("/temp", StaticFiles(directory=temp_files_dir), name="temp")')

with open('apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(content)
