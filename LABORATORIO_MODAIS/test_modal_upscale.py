import httpx
import json

url = "https://canalobservadoreconomico--apollo-render-router-apollo-api.modal.run/generate/image"
payload = {
    "prompt": "A hyper-realistic cinematic shot of a futuristic cyberpunk boy hacker at a neon desk, 8K, detailed, dramatic lighting",
    "model": "flux2-universal",
    "format": "horizontal",
    "use_upscale": True
}

with httpx.stream("POST", url, json=payload, timeout=600.0) as r:
    for line in r.iter_lines():
        if line:
            print(line)
