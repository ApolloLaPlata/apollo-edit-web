import asyncio
import httpx
import json
import base64

async def test():
    keys = [
        "sk-lit-8d672728-66a9-467f-9430-8438dbdf2380",
        "sk-lit-3d061abb-d92d-4d66-a79a-7474664caf81",
        "sk-lit-de1aaa27-2e2c-489e-9d1d-90b9127eb398",
        "sk-lit-baf54912-3c66-4e6d-88cf-00b93868c9a0"
    ]

    llm_prompt = "Hello"
    async with httpx.AsyncClient(timeout=10.0) as lc:
        for k in keys:
            try:
                print(f"Testing key {k[:15]}...")
                llm_res = await lc.post(
                    "https://lightning.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
                    json={
                        "model": "nvidia-nemotron-3-ultra-550b-a55b",
                        "messages": [{"role": "user", "content": llm_prompt}]
                    }
                )
                if llm_res.status_code == 200:
                    print("WORKS!")
                else:
                    print(f"Error {llm_res.status_code}")
            except Exception as e:
                print(e)
asyncio.run(test())
