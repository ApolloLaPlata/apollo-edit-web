import httpx
import asyncio

async def run_tests():
    # TESTE 1: Batch Generator
    try:
        url = "http://163.176.135.59/api/music/generate_batch_ideas"
        print(f"Testando {url}...")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json={"theme": "2 músicas de trap triste sobre saudade", "count": 2})
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")
    except Exception as e:
        print(f"Erro Batch: {e}")

    print("\n----------------\n")
    
    # TESTE 2: Auto-Tag
    try:
        url2 = "http://163.176.135.59/api/music/auto_tag_lyrics"
        print(f"Testando {url2}...")
        async with httpx.AsyncClient(timeout=60) as client:
            raw_lyric = "Hoje eu acordei mal\nSem você aqui é tão letal\nMas eu vou superar\nE um novo dia vai brilhar"
            resp2 = await client.post(url2, json={"lyrics": raw_lyric})
            print(f"Status: {resp2.status_code}")
            print(f"Body: {resp2.text}")
    except Exception as e:
        print(f"Erro Auto-Tag: {e}")

asyncio.run(run_tests())
