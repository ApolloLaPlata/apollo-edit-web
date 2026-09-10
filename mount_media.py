import sys
import os

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add static files mount for media
if 'from fastapi.staticfiles import StaticFiles' not in text:
    text = text.replace('from fastapi import FastAPI', 'from fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles')

if 'app.mount("/media"' not in text:
    # Find the app = FastAPI() line and add it after
    text = text.replace('app = FastAPI(title="Apollo Web", docs_url="/api/docs", openapi_url="/api/openapi.json")',
                        'app = FastAPI(title="Apollo Web", docs_url="/api/docs", openapi_url="/api/openapi.json")\n\nimport os\nos.makedirs("/home/ubuntu/apollo_edit/media", exist_ok=True)\napp.mount("/media", StaticFiles(directory="/home/ubuntu/apollo_edit/media"), name="media")')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)
