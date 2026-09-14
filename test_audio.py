import httpx
import asyncio

async def test():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "http://163.176.135.59/api/audio/generate",
                json={"prompt": "teste de beat cyberpunk brasileiro", "engine": "acestep", "duration": 10, "lyrics": "O futuro eh loko"}
            )
            print("Status:", resp.status_code)
            # Imprimir so um pedaco
            print("Body:", resp.text[:200])
    except httpx.ReadTimeout:
        print("Timeout! (Significa que chegou na Modal e esta gerando!!)")
    except Exception as e:
        print("Erro:", e)

asyncio.run(test())
