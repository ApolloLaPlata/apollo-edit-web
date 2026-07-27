import asyncio
import httpx
import time

async def test():
    print("Iniciando teste END-TO-END...")
    print("Rota: Vercel (apolloedit.com) -> Oracle VPS -> Modal -> ComfyUI")
    start = time.time()
    async with httpx.AsyncClient(follow_redirects=True) as client:
        res = await client.post("https://apolloedit.com/api/studio/modal/generate_image", json={
            "prompt": "An astronaut riding a futuristic motorcycle on Mars, 8k resolution, photorealistic",
            "model": "flux2-universal",
            "format": "horizontal",
            "steps": 20
        }, timeout=300.0)
        end = time.time()
        print(f"Status code: {res.status_code}")
        print(f"Final URL: {res.url}")
        print(f"Tempo total (Vercel -> Oracle -> Modal -> Oracle -> Vercel): {end - start:.2f}s")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                print("SUCESSO! Imagem recebida com sucesso da ponta da Vercel.")
            else:
                print("ERRO no payload:", data)
        else:
            print("Response:", res.text[:500])

asyncio.run(test())
