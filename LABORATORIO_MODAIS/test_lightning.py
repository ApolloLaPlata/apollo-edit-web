import httpx
import asyncio

async def test():
    try:
        url = "https://apollolaplata--lightning-proxy.modal.run/v1/chat/completions"
        payload = {
            "model": "meta-llama/Llama-3-70b-chat-hf",
            "messages": [{"role": "user", "content": "Olá, me dê um oi!"}]
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            print("Status:", resp.status_code)
            print("Body:", resp.text)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
