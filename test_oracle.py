import asyncio
import httpx
import time

async def test_direct_oracle():
    url = "http://163.176.135.59/api/studio/modal/generate/audio_lab"
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
    
    print("Enviando via ORACLE (esperando chunks)...", flush=True)
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                print(f"Status: {resp.status_code}", flush=True)
                async for chunk in resp.aiter_lines():
                    print(f"Chunk recebido: {chunk}", flush=True)
        except Exception as e:
            print(f"Error: {e}", flush=True)

asyncio.run(test_direct_oracle())
