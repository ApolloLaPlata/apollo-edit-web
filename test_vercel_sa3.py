import httpx
import asyncio
import json
import time

async def test():
    print("Iniciando requisicao SA3 para Vercel...")
    t0 = time.time()
    async with httpx.AsyncClient(timeout=300.0) as client:
        req_headers = {'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026'}
        body = json.dumps({"prompt": "trap dark type beat, heavy bass", "model": "sa3", "duration": 10, "lyrics": ""})
        vercel_url = "https://www.apolloedit.com.br/api/studio/modal/generate/audio_lab"
        
        async with client.stream("POST", vercel_url, content=body.encode('utf-8'), headers=req_headers) as response:
            print("Conectado! Status:", response.status_code)
            async for chunk in response.aiter_bytes():
                print(f"[{time.time()-t0:.1f}s] CHUNK: {chunk[:100]}")

asyncio.run(test())
