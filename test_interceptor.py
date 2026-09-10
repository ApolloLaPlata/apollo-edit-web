import httpx
import asyncio
import json

async def test():
    req_headers = {'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026'}
    body = json.dumps({"prompt": "trap dark", "model": "Stable Audio 3 Medium (Instrumental & SFX)", "duration": 30, "lyrics": "[Verse 1]\\nAcordei cedo pra vencer..."}).encode('utf-8')
    modal_url = "https://historiasde7dias--apollo-render-router-apollo-api.modal.run/generate/audio_lab"
    
    async with httpx.AsyncClient(timeout=1200.0) as local_client:
        task = asyncio.create_task(local_client.post(modal_url, content=body, headers=req_headers))
        
        while not task.done():
            print("PING")
            await asyncio.sleep(5)
            
        response = task.result()
        print("STATUS:", response.status_code)
        
        if response.status_code != 200:
            print("RETURNING:", response.content)
            return
        
        data = response.json()
        print("DATA:", data)
        if data.get("status") == "success" and "audio_base64" in data:
            print("SUCCESS BRANCH")
        else:
            print("ERROR BRANCH")
            result = response.content + b'\n'
            print("YIELDING:", result[:100])

asyncio.run(test())
