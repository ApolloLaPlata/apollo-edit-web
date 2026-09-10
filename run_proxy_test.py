import requests
import base64
import json

def run():
    img_paths = [
        r"C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\.user_uploaded\media_1788820369071.jpg",
        r"C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\.user_uploaded\media_1788820454970.png"
    ]
    b64s = []
    for p in img_paths:
        with open(p, "rb") as f:
            b64s.append("data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8"))
            
    payload = {
        "model": "qwen-image",
        "prompt": "A mulher de blusa amarela conversando na rua com a mulher negra de leggings pretas.",
        "reference_images_base64": b64s,
        "aspect_ratio": "horizontal",
        "dynamic_steps": False # This avoids skipping the LLM check if dynamic_steps was set
    }
    
    print("Enviando para o Proxy (Oracle VPS)...")
    url = "http://163.176.135.59:8000/api/studio/modal/generate"
    # To just test the prompt generation and not wait for the 30s image generation, 
    # we'll use a timeout or we just let it run and look at the logs!
    # Wait, the proxy doesn't return the LLM output in the JSON response, it returns the generated image.
    # To see the LLM output, we need to read the server logs!
    try:
        r = requests.post(url, json=payload, timeout=2) # Force timeout to just trigger it
    except requests.exceptions.ReadTimeout:
        print("Requisicao disparada. Vamos checar os logs na VPS agora.")

if __name__ == "__main__":
    run()
