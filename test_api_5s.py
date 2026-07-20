import requests, base64, json, time
with open(r'C:\Users\v5est\.gemini\antigravity\brain\0e14241d-91af-4860-8795-5ae227d39bc9\cyber_warrior_1782252020651.png', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode('utf-8')
payload = {'model': 'ltx', 'preset': 'pro', 'duration': 5, 'prompt': 'Cyber warrior striking with a glowing sword in rain', 'image_base64': img_b64}
print('Enviando req PRO 5s...')
start=time.time()
r = requests.post('https://roxingo--apollo-render-router-apollo-api.modal.run/generate/video', json=payload, stream=True)
for line in r.iter_lines():
    if line:
        data = line.decode('utf-8')
        print(data[:200])
        if 'video_base64' in data:
            obj = json.loads(data)
            with open('cyber_warrior_5s.mp4', 'wb') as f:
                f.write(base64.b64decode(obj['video_base64']))
            print('Video saved!')
print('Total time:', time.time()-start)

