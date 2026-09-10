import sys
import time
import base64
import requests

def testar_direto():
    url = "https://roxingo--apollo-render-router-apollo-api.modal.run/generate/image"
    print('Acessando URL:', url)
    
    payload = {
        'prompt': 'A cinematic ultra-realistic 4k shot of a futuristic cyberpunk city with flying cars',
        'reference_images_base64': [],
        'aspect_ratio': 'horizontal',
        'model': 'qwen-image',
        'preset': 'fast',
        'steps': 28,
        'use_upscale': False,
        'format': 'image/jpeg'
    }
    
    t0 = time.time()
    r = requests.post(url, json=payload)
    data = r.json()
    job_id = data.get('job_id')
    if not job_id:
        print('Erro: Sem job_id!', data)
        return
        
    print('Job ID obtido:', job_id)
    print('Iniciando polling...')
    
    while True:
        s = requests.get(f"https://roxingo--apollo-render-router-apollo-api.modal.run/status/{job_id}")
        s_data = s.json()
        if s_data.get('status') == 'success':
            import json
            content = json.loads(s_data.get('content'))
            if content.get('status') == 'success':
                t_total = time.time() - t0
                print(f'SUCESSO! Tempo total: {t_total:.2f} segundos.')
                img_b64 = content.get('image_base64')
            else:
                print('Erro no container:', content)
            break
        elif s_data.get('status') == 'error':
            print('ERRO:', s_data)
            break
        print('Processando...')
        time.sleep(3)

if __name__ == '__main__':
    testar_direto()
