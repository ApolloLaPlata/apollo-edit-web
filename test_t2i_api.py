
import requests
import json
import base64
import time

url = "https://historiasde7dias--apollo-render-router-apollo-api.modal.run/generate/image"

payload = {
    "prompt": "A highly detailed cinematic shot of a futuristic cyberpunk hacker coding in a neon-lit room, 8k resolution, photorealistic",
    "format": "horizontal",
    "model": "qwen-image",
    "reference_images_base64": []
}

print("Enviando request para T2I (Qwen Image Engine)...")
res = requests.post(url, json=payload)
data = res.json()

if data.get("status") == "success":
    job_id = data.get("job_id")
    print(f"Job enfileirado: {job_id}. Aguardando...")
    
    # Wait for completion via status endpoint (simulating the frontend)
    # Actually, we can just use the ArenaComfyEngine logic to fetch the result.
    # But since the router returns a job_id (fc object_id), we need to check its status.
    # Wait, the frontend checks status by hitting some endpoint or we can just run the test directly via modal call.
    # Let us just call the QwenImageEngine directly to make the test faster and easier to fetch the image.

