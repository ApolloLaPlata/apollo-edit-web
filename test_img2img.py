import requests, base64, json, time, os

# Use a test image
image_path = r'C:\Users\v5est\.gemini\antigravity\brain\0e14241d-91af-4860-8795-5ae227d39bc9\cyber_warrior_1782252020651.png'
if not os.path.exists(image_path):
    print("Imagem nao encontrada.")
    exit()

with open(image_path, 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode('utf-8')

payload = {
    'prompt': 'A high quality realistic rendering of a cyber warrior',
    'reference_images_base64': [img_b64],
    'format': 'horizontal',
    'model': 'flux2-universal'
}

print('Enviando req Img2Img...')
start=time.time()
r = requests.post('https://macacodriver--apollo-render-router-apollo-api.modal.run/generate/image', json=payload, stream=True)
for line in r.iter_lines():
    if line:
        decoded = line.decode('utf-8')
        if "data: " in decoded:
            try:
                data = json.loads(decoded.split("data: ")[1])
                if "url" in data:
                    print(f"Sucesso! Imagem em: {data['url']}")
                    print(f"Tempo total (API): {time.time()-start:.2f}s")
                    break
                elif "heartbeat" not in decoded:
                    print(data)
            except Exception as e:
                print("Error parsing json:", e)
        else:
            print(decoded)
print(f'Fim do script. Tempo total: {time.time()-start:.2f}s')
