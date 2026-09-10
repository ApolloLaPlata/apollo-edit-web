import asyncio
import httpx
import time

async def test_vercel_proxy():
    url = "https://www.apolloedit.com.br/api/studio/modal/generate/audio_lab"
    payload = {
        "prompt": "trap dark short final test",
        "lyrics": "",
        "model": "sa3",
        "duration": 5
    }
    headers = {
        "Content-Type": "application/json",
        "x-apollo-lock": "apollo-beta-key-2026"
    }
    
    print("Enviando via Vercel (esperando chunks)...")
    t0 = time.time()
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                print(f"Status: {resp.status_code}")
                async for chunk in resp.aiter_lines():
                    print(f"Chunk recebido: {chunk}")
                    if "audio_url" in chunk:
                        import json
                        data = json.loads(chunk)
                        file_url = data['audio_url']
                        print(f"Fetching audio file from {file_url}...")
                        file_resp = await client.get(file_url)
                        print(f"File Status: {file_resp.status_code}")
                        print(f"File Size: {len(file_resp.content)}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_vercel_proxy())
