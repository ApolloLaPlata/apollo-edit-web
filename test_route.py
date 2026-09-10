import sys
with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r') as f:
    text = f.read()

new_route = '''
@app.get("/api/test_route")
def test_route():
    return {"status": "ok"}
'''

if "/api/test_route" not in text:
    text = text.replace('app = FastAPI(', 'app = FastAPI()\n' + new_route + '\n#')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w') as f:
    f.write(text)
