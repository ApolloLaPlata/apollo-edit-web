import asyncio
import httpx
import time
import json

async def test():
    print("Iniciando teste batendo DIRETO no IP DO ORACULO (163.176.135.59:8000)...")
    start = time.time()
    async with httpx.AsyncClient(timeout=300.0) as client:
        res = await client.post("http://163.176.135.59:8000/api/studio/modal/generate_image", json={
            "prompt": "A cute robotic dog running in a cyber city, 8k resolution",
            "model": "flux2-universal",
            "format": "horizontal",
            "steps": 20
        }, timeout=300.0)
        end = time.time()
        print(f"Status code: {res.status_code}")
        print(f"Tempo total (Oracle -> Modal -> Oracle): {end - start:.2f}s")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                print("SUCESSO ABSOLUTO! Imagem gerada e retornada do Oraculo sem proxy!")
            else:
                print("ERRO no payload:", data)
        else:
            print("Response:", res.text[:500])

asyncio.run(test())
