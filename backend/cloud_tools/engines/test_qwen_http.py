import sys
import time
import base64
import requests

def testar_direto():
    url = "https://roxingo--apollo-render-router-apollo-api.modal.run/generate/image"
    print('Acessando URL:', url)
    
    from PIL import Image
    import io
    blank = Image.new("RGB", (1280, 720), (255, 255, 255))
    buf = io.BytesIO()
    blank.save(buf, format="PNG")
    img1_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    payload = {
        'prompt': 'A cinematic ultra-realistic 4k shot of a futuristic cyberpunk city with flying cars',
        'reference_images_base64': [img1_b64],
        'aspect_ratio': 'horizontal',
        'model': 'qwen-image',
        'preset': 'fast',
        'steps': 28,
        'use_upscale': False,
        'format': 'image/jpeg'
    }
    
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
                print('SUCESSO!')
                img_b64 = content.get('image_base64')
                out_path = r'C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\teste_qwen_ROXINGO.jpg'
                with open(out_path, 'wb') as img_f:
                    img_f.write(base64.b64decode(img_b64))
                print('IMAGEM SALVA EM:', out_path)
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
