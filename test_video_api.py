
import requests
import time
import json

def test_wan_video():
    print("Iniciando teste de Video (Wan2.1) via API na VPS...")
    url = "https://api.apolloedit.com.br/api/studio/modal/generate_video"
    payload = {
        "prompt": "Cinematic shot of a cybernetic glowing cat walking in a dark alley, 4k",
        "aspect_ratio": "horizontal",
        "model": "wan",
        "preset": "fast"
    }
    
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        print("Resposta recebida:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Erro:", e)
        return

if __name__ == "__main__":
    test_wan_video()

