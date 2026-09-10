import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

debug_route = '''
@app.get("/debug_routes")
def get_routes():
    return {"routes": [{"path": r.path, "name": r.name, "methods": getattr(r, 'methods', None)} for r in app.routes]}
'''

code = code.replace('@app.post("/api/music/auto_tag_lyrics")', debug_route + '\n@app.post("/api/music/auto_tag_lyrics")')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)
