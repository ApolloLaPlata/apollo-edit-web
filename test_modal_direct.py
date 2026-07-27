import asyncio
import httpx
import base64
import time

async def test():
    print("Iniciando requisicao COLD START para Modal...")
    t0 = time.time()
    async with httpx.AsyncClient(timeout=600.0, follow_redirects=True) as client:
        headers = {}
        res = await client.post("https://canalobservadoreconomico--apollo-render-router-apollo-api.modal.run/generate/image", json={
            "prompt": "a beautiful landscape of mountains at sunset, detailed, vibrant colors, version 8",
            "seed": 333333,
            "model": "flux2-universal",
            "format": "horizontal",
            "steps": 20,
            "use_upscale": False
        }, headers=headers)
        
        tf = time.time() - t0
        print(f"Status code: {res.status_code}, Tempo Total: {tf:.2f}s")
        
        if res.status_code == 200:
            lines = [line.strip() for line in res.text.split("\n") if line.strip()]
            if lines:
                import json
                try:
                    data = json.loads(lines[-1])
                    if data.get("status") == "success":
                        b64_data = data.get("image_base64")
                        if b64_data:
                            with open("test_modal_output.png", "wb") as f:
                                f.write(base64.b64decode(b64_data))
                            print("SUCESSO: Imagem salva em test_modal_output.png!")
                except Exception as e:
                    print("ERRO ao parsear JSON:", e, lines[-1])

asyncio.run(test())
