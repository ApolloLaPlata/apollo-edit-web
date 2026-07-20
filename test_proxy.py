import asyncio
import httpx
async def run():
    client = httpx.AsyncClient(timeout=1200.0)
    req = client.build_request('POST', 'https://apollolaplata--apollo-render-router-apollo-api.modal.run/generate/image', content=b'{\"prompt\":\"test\"}', headers={'Content-Type':'application/json'})
    try:
        async with client.send(req, stream=True) as response:
            async for chunk in response.aiter_bytes():
                print(chunk)
    except Exception as e:
        print('Error:', e)
asyncio.run(run())
