import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient(timeout=120.0) as client:
        req_headers = {'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026'}
        body = json.dumps({"prompt": "trap dark", "model": "Stable Audio 3 Medium (Instrumental & SFX)", "duration": 30, "lyrics": "[Verse 1]\\nAcordei cedo pra vencer..."})
        modal_url = "https://historiasde7dias--apollo-render-router-apollo-api.modal.run/generate/audio_lab"
        response = await client.post(modal_url, content=body.encode('utf-8'), headers=req_headers)
        print("STATUS:", response.status_code)
        try:
            print("DATA KEYS:", response.json().keys())
            if "status" in response.json():
                print("STATUS VALUE:", response.json()["status"])
            if "message" in response.json():
                print("MESSAGE:", response.json()["message"])
            if "audio_url" in response.json():
                print("AUDIO_URL:", response.json()["audio_url"])
        except Exception as e:
            print("TEXT:", response.text[:200])

asyncio.run(test())
