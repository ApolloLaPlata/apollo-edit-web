import httpx
import json

url = 'https://canalobservadoreconomico--apollo-render-router-apollo-api.modal.run/generate/image'
payload = {
    'prompt': 'A hyper-realistic cinematic shot of a futuristic cyberpunk boy hacker at a neon desk, 8K, detailed, dramatic lighting',
    'model': 'flux2-universal',
    'format': 'horizontal',
    'use_upscale': False
}
headers = {
    'Authorization': 'Bearer ws-kdsrElfoXzqOwifhCR3v4Y'
}

with httpx.Client(timeout=600.0) as client:
    with client.stream('POST', url, json=payload, headers=headers) as r:
        for line in r.iter_lines():
            if line.strip():
                try:
                    data = json.loads(line)
                    if isinstance(data, dict) and 'image_base64' in data:
                        with open('test_base.json', 'w') as f:
                            json.dump(data, f)
                except: pass
