import asyncio
import httpx
import time

async def test_vercel_proxy():
    url = "https://www.apolloedit.com.br/api/studio/modal/generate/audio_lab"
    payload = {
        "prompt": "trap dark short test 3",
        "lyrics": "",
        "model": "sa3",
        "duration": 5
    }
    headers = {
        "Content-Type": "application/json",
        "x-apollo-lock": "apollo-beta-key-2026"
    }
    
    print("Enviando via Vercel (esperando audio_url)...")
    t0 = time.time()
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            data = resp.json()
            print(f"Data chaves: {list(data.keys())}")
            if data.get('audio_url'):
                print(f"URL retornada: {data['audio_url']}")
                file_resp = await client.get(data['audio_url'])
                print(f"File Status (via /media/ rewrite): {file_resp.status_code}")
                print(f"File Size: {len(file_resp.content)}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_vercel_proxy())
