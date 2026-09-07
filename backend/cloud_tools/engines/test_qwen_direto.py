import sys
import os
import time
import base64

os.environ['MODAL_TOKEN_ID'] = 'ak-6pDTu1xBPp1jPG08LXK1K8'
os.environ['MODAL_TOKEN_SECRET'] = 'as-f8CE8vvKRJdL8BODP1FSkj'

import modal

def testar_direto():
    print('Acessando funcao Qwen diretamente na Roxingo...')
    
    f = modal.Function.from_name("apollo-render-router", "api_generate_image")
    
    payload = {
        'prompt': 'A cinematic ultra-realistic 4k shot of a futuristic cyberpunk city with flying cars',
        'aspect_ratio': 'horizontal',
        'model': 'qwen-image',
        'preset': 'fast',
        'steps': 28,
        'use_upscale': False
    }
    
    print('Enviando geracao (bypassing VPS)...')
    try:
        t0 = time.time()
        res = f.remote(payload)
        tf = time.time() - t0
        print('Resposta completa em', round(tf,2), 'segundos!')
        
        if res.get('status') == 'success':
            img_b64 = res.get('image_base64')
            if img_b64:
                out_path = r'C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\teste_qwen_ROXINGO.jpg'
                with open(out_path, 'wb') as img_f:
                    img_f.write(base64.b64decode(img_b64))
                print('IMAGEM SALVA!')
            else:
                print('Sucesso mas sem base64.')
        else:
            print('Erro retornado:', res)
    except Exception as e:
        print('Erro fatal na execucao remota:', e)

if __name__ == '__main__':
    testar_direto()
