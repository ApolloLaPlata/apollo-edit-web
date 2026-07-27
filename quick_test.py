import time, urllib.request, json
t0 = time.time()
url = "https://canalobservadoreconomico--apollo-render-router-apollo-api.modal.run/generate/image"
payload = json.dumps({
    "prompt": "a futuristic neon sports car racing on a wet Tokyo street at night, cinematic lighting, 8k",
    "model": "flux2-universal",
    "format": "horizontal",
    "upscale": True
}).encode("utf-8")
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
print("Sending request to Modal H100...")
res = urllib.request.urlopen(req, timeout=300)
data = json.loads(res.read().decode("utf-8"))
print(f"Time: {time.time()-t0:.2f}s | Status: {data.get('status')} | Has Image: {len(data.get('image_base64', '')) > 1000}")
if data.get('image_base64'):
    import base64
    with open("test_flux_result.png", "wb") as f:
        f.write(base64.b64decode(data['image_base64']))
    print("Saved test_flux_result.png!")
