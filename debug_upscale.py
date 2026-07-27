import httpx
import json

url = "https://canalobservadoreconomico--apollo-render-router-apollo-api.modal.run/generate/image"
payload = {
    "prompt": "A hyper-realistic cinematic shot of a futuristic cyberpunk boy hacker at a neon desk, 8K, detailed, dramatic lighting",
    "model": "flux2-universal",
    "format": "horizontal",
    "use_upscale": True
}
headers = {
    "Authorization": "Bearer ws-kdsrElfoXzqOwifhCR3v4Y"
}

print("Iniciando requisicao...")
try:
    with httpx.Client(timeout=600.0) as client:
        with client.stream("POST", url, json=payload, headers=headers) as r:
            for line in r.iter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        print("Received data keys:", data.keys() if isinstance(data, dict) else type(data))
                        print("Raw data:", str(data)[:100])
                        if isinstance(data, dict) and "image_base64" in data:
                            with open("test_output_upscale.json", "w") as f:
                                json.dump(data, f)
                            print("Saved to test_output_upscale.json")
                    except:
                        print("Raw text:", str(line)[:100])
                    print("Received line length:", len(line))
except Exception as e:
    print(f"Erro: {e}")
