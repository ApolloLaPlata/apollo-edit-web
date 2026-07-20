import requests, base64, json, time
image_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_todos_modelos\cyber_warrior_landscape.png"
with open(image_path, 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode('utf-8')
print('Enviando req FINAL...')
r = requests.post('https://apollolaplata--apollo-render-router-api-generate-video.modal.run', json={'prompt': 'Cyber warrior standing strong, looking directly at the camera, steady camera, highly detailed face, realistic textures, cinematic lighting, 4k, subtle natural movement, no morphing, stable background', 'image_base64': f'data:image/png;base64,{img_b64}', 'model': 'ltx', 'preset': 'pro', 'duration': 5, 'steps': 50}, stream=True)
for line in r.iter_lines():
    if line:
        try:
            d = json.loads(line.decode('utf-8'))
            if 'video_base64' in d:
                output_file = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/testes_todos_modelos/cyber_warrior_final.mp4"
                with open(output_file, 'wb') as f:
                    f.write(base64.b64decode(d['video_base64']))
                print('VIDEO SALVO! Tempo:', d.get('render_time_seconds'))
            else:
                print('Atualizacao:', d)
        except:
            print('RAW:', line)
