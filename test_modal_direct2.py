import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        res = await client.post("https://canalobservadoreconomico--apollo-render-router-apollo-api.modal.run/generate/image", json={
            "prompt": "test direct modal 2",
            "model": "flux2-universal",
            "format": "horizontal",
            "steps": 20
        }, timeout=300.0)
        print("Status code:", res.status_code)
        print("Response:", res.text)

asyncio.run(test())
