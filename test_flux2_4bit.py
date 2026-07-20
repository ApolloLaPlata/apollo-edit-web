import requests, json, time, base64

url = 'https://macacodriver--apollo-render-router-apollo-api.modal.run/generate/image'
payload = {
    'model': 'flux2-universal',
    'prompt': 'cartoon caricature style, Elon Musk smiling, riding a golden bicycle on a sunny beach, wearing dark navy suit, big head caricature art style, vibrant colors, clean lines, high quality illustration',
    'format': 'square',
    'seed': 42
}

print('[TEST] Disparando FLUX.2 4-bit Python Puro H100...', flush=True)
t0 = time.time()
try:
    r = requests.post(url, json=payload, timeout=600, stream=True)
    elapsed = time.time() - t0
    print(f'[HTTP] Status: {r.status_code} | {elapsed:.1f}s', flush=True)
    result = None
    for line in r.iter_lines():
        if line:
            elapsed = time.time() - t0
            print(f'[CHUNK] {elapsed:.1f}s | {len(line)} bytes', flush=True)
            try:
                result = json.loads(line)
            except:
                pass
    elapsed = time.time() - t0
    if result and result.get('image_base64'):
        img_data = base64.b64decode(result['image_base64'])
        out = 'testes_modal_output/flux2_4bit_h100_test.png'
        with open(out, 'wb') as f:
            f.write(img_data)
        render_time = result.get('render_time_seconds', '?')
        print(f'[OK] Salvo em {out} | Total: {elapsed:.1f}s | Render: {render_time}s', flush=True)
    else:
        print(f'[ERRO] Resultado: {json.dumps(result)[:300]}', flush=True)
except Exception as e:
    elapsed = time.time() - t0
    print(f'[ERRO] {type(e).__name__}: {e} | {elapsed:.1f}s', flush=True)
