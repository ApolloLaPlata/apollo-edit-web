import requests, base64, json, time
with open(r'C:\Users\v5est\.gemini\antigravity\brain\0e14241d-91af-4860-8795-5ae227d39bc9\cyber_warrior_1782252020651.png', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode('utf-8')
payload = {'model': 'ltx', 'preset': 'fast', 'duration': 2, 'prompt': 'Cyber warrior striking with a glowing sword in rain', 'image_base64': img_b64}
print('Enviando req... (aguardando snapshot 3 mins)')
start=time.time()
r = requests.post('https://roxingo--apollo-render-router-apollo-api.modal.run/generate/video', json=payload, stream=True)
for line in r.iter_lines():
    if line:
        print(line.decode('utf-8'))
print('Total time:', time.time()-start)

