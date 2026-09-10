import httpx
import asyncio

async def test():
    url = 'http://163.176.135.59/api/studio/modal/generate/audio_lab'
    payload = {
        'prompt': 'A beautiful test song',
        'lyrics': '[Verse 1]\nTest test',
        'model': 'sa3',
        'duration': 5,
        'reference_audio_base64': None
    }
    headers = {
        'Content-Type': 'application/json',
        'x-apollo-lock': 'apollo-beta-key-2026'
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Sending request to Oracle Proxy...")
        res = await client.post(url, json=payload, headers=headers)
        print("Oracle Proxy responded:", res.status_code, res.text)
        
    async with httpx.AsyncClient(timeout=30.0) as client:
        url_direct = 'https://historiasde7dias--apollo-render-router-apollo-api.modal.run/generate/audio_lab'
        print("Sending request direct to Modal...")
        res = await client.post(url_direct, json=payload, headers=headers)
        print("Modal Direct responded:", res.status_code, res.text[:100])

asyncio.run(test())
