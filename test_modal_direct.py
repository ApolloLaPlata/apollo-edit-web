import httpx
import asyncio

async def test():
    url = 'https://historiasde7dias--apollo-render-router-apollo-api.modal.run/generate/audio_lab'
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
        print("Sending request...")
        res = await client.post(url, json=payload, headers=headers)
        print("Status:", res.status_code)
        print("Response:", res.text)

asyncio.run(test())
