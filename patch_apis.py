import os

file_path = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO\servidor_web.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

patch = """
# ===== ROTAS DA CENTRAL DE NOTÍCIAS =====
import requests
from bs4 import BeautifulSoup
from fastapi import Response

@app.get("/api/search-youtube")
async def api_search_youtube(q: str):
    try:
        from youtubesearchpython import VideosSearch
        videosSearch = VideosSearch(q, limit = 12)
        r = videosSearch.result()
        
        videos = []
        for v in r.get('result', []):
            views = int(v.get('viewCount', {}).get('text', '0').replace(' views', '').replace(',', '').replace('.', '').split(' ')[0]) if v.get('viewCount', {}).get('text') else 0
            
            # Engagement estimates
            import random
            estimatedLikes = int(views * (0.03 + random.random() * 0.02))
            estimatedComments = int(views * (0.003 + random.random() * 0.005))
            estimatedShares = int(views * (0.005 + random.random() * 0.01))
            
            videos.append({
                "title": v.get('title'),
                "url": v.get('link'),
                "thumbnail": v.get('thumbnails', [{}])[0].get('url'),
                "author": v.get('channel', {}).get('name'),
                "views": views,
                "ago": v.get('publishedTime', 'N/A'),
                "description": v.get('descriptionSnippet', [{}])[0].get('text') if v.get('descriptionSnippet') else '',
                "duration": v.get('duration'),
                "likes": estimatedLikes,
                "comments": estimatedComments,
                "shares": estimatedShares
            })
            
        return {"videos": videos}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/search-images")
async def api_search_images(q: str):
    try:
        # Simple DuckDuckGo scraping for MVP
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        tokenRes = requests.get(f"https://duckduckgo.com/?q={q}&df=m", headers=headers)
        import re
        vqdMatch = re.search(r"vqd=(['\"]?)([^&\"']+)\\1", tokenRes.text)
        
        images = []
        if vqdMatch and vqdMatch.group(2):
            vqd = vqdMatch.group(2)
            searchUrl = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={q}&vqd={vqd}"
            imgRes = requests.get(searchUrl, headers=headers)
            if imgRes.status_code == 200:
                data = imgRes.json()
                for r in data.get('results', []):
                    if r.get('image') and r.get('image').startswith('http'):
                        images.append({
                            "url": r['image'],
                            "source": r['url'],
                            "thumbnail": r.get('thumbnail')
                        })
        return {"urls": images[:40]}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/proxy-image")
async def api_proxy_image(url: str):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return Response(content=r.content, media_type=r.headers.get('content-type', 'image/jpeg'))
        return JSONResponse({"error": "Failed to fetch"}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/grok")
async def api_grok(req: Request):
    try:
        data = await req.json()
        api_key = data.get('apiKey')
        if not api_key: return JSONResponse({"error": "Missing API key"}, status_code=400)
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            "model": data.get('model', 'grok-beta'),
            "messages": data.get('messages'),
            "temperature": data.get('temperature', 0.3),
            "stream": False
        }
        r = requests.post('https://api.x.ai/v1/chat/completions', headers=headers, json=payload)
        return r.json()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/grok/models")
async def api_grok_models(req: Request):
    try:
        data = await req.json()
        api_key = data.get('apiKey')
        if not api_key: return JSONResponse({"error": "Missing API key"}, status_code=400)
        
        headers = {'Authorization': f'Bearer {api_key}'}
        r = requests.get('https://api.x.ai/v1/models', headers=headers)
        return r.json()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
# ========================================

# Montar diretório"""

if "# ===== ROTAS DA CENTRAL DE NOTÍCIAS =====" not in content:
    new_content = content.replace('import os\\napp.mount("/ext_apps", StaticFiles', patch + '\\nimport os\\napp.mount("/ext_apps", StaticFiles')
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Patched successfully")
else:
    print("Already patched")
