import requests, json, time, base64

url = 'https://macacodriver--apollo-render-router-apollo-api.modal.run/generate/image'
img_path = r"C:\Users\v5est\Downloads\Gemini_Generated_Image_2ul6s52ul6s52ul6.png"

try:
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
except Exception as e:
    print(f"[ERRO] Falha ao ler a imagem: {e}")
    exit(1)

payload = {
    'model': 'flux2-universal',
    'prompt': 'estilo desenho 2D cartoon, arte vetorial flat. Uma unica mulher bonita de terno azul escuro e camisa branca, cabelos loiros, andando de bicicleta na praia.',
    'format': 'square',
    'seed': 42,
    'reference_images_base64': [img_b64]
}

print('[TEST] Disparando FLUX.2 ComfyUI (Teste Real de Produção)...', flush=True)
t0 = time.time()
try:
    r = requests.post(url, json=payload, timeout=600, stream=True)
    elapsed = time.time() - t0
    print(f'[HTTP] Status: {r.status_code} | Resposta inicial da Nuvem (Cold Start Mitigation): {elapsed:.2f}s', flush=True)
    
    result = None
    for line in r.iter_lines():
        if line:
            chunk_time = time.time() - t0
            # A API retorna um JSON vazio (" \n") como keep-alive a cada 5s
            if len(line) > 5:
                try:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        result = data
                except:
                    pass
                
    total_time = time.time() - t0
    if result and 'image_base64' in result:
        img_data = base64.b64decode(result['image_base64'])
        out = r'C:\Users\v5est\Downloads\resultado_boteco_rio.png'
        with open(out, 'wb') as f:
            f.write(img_data)
        
        # Custo Modal H100 é aprox $4.32 por hora ($0.0012 por segundo)
        cost = total_time * 0.0012
        
        print(f'[OK] Imagem salva em {out}')
        print(f'[MÉTRICAS] Tempo total: {total_time:.1f}s')
        print(f'[MÉTRICAS] Tempo de renderização (Backend): {result.get("render_time_seconds", 0)}s')
        print(f'[MÉTRICAS] Custo estimado na H100: ${cost:.5f}')
    else:
        print(f"[ERRO] Resultado inesperado: {result}")
except Exception as e:
    elapsed = time.time() - t0
    print(f'[ERRO] {type(e).__name__}: {e} | {elapsed:.1f}s', flush=True)
