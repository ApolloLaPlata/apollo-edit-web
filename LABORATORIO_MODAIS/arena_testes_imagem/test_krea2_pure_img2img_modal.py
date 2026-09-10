import json
import base64
import os
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_krea2_img2img():
    print('Iniciando Krea-2 Img2Img PURO (sem mascara, sem PuLID)...')
    
    img_path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/referencia_bombadao.jpg'
    with open(img_path, 'rb') as f:
        input_data = f.read()
    
    img_b64 = base64.b64encode(input_data).decode('utf-8')
    
    workflow = {
        '1': { 'class_type': 'UNETLoader', 'inputs': { 'unet_name': 'Krea-2-Raw.safetensors', 'weight_dtype': 'default' }},
        '2': { 'class_type': 'DualCLIPLoader', 'inputs': { 'clip_name1': 't5xxl_fp16.safetensors', 'clip_name2': 'clip_l.safetensors', 'type': 'flux' }},
        '3': { 'class_type': 'VAELoader', 'inputs': { 'vae_name': 'ae.safetensors' }},
        
        '4': { 'class_type': 'LoadImage', 'inputs': { 'image': 'referencia.jpg' }},
        '5': { 'class_type': 'VAEEncode', 'inputs': { 'pixels': ['4', 0], 'vae': ['3', 0] }},
        
        '6': { 'class_type': 'CLIPTextEncode', 'inputs': { 'text': 'a cinematic photo of a muscular man wearing a black beanie and punisher tank top, riding a mountain bike on a sunny beach boardwalk', 'clip': ['2', 0] }},
        
        '7': { 'class_type': 'FluxGuidance', 'inputs': { 'guidance': 3.5, 'conditioning': ['6', 0] }},
        
        '8': { 'class_type': 'KSampler', 'inputs': {
            'model': ['1', 0],
            'positive': ['7', 0],
            'negative': ['6', 0],
            'latent_image': ['5', 0],
            'seed': 888, 'steps': 25, 'cfg': 1.0, 'sampler_name': 'euler', 'scheduler': 'simple', 'denoise': 0.65
        }},
        
        '9': { 'class_type': 'VAEDecode', 'inputs': { 'samples': ['8', 0], 'vae': ['3', 0] }},
        '10': { 'class_type': 'SaveImage', 'inputs': { 'images': ['9', 0], 'filename_prefix': 'krea2_img2img_puro' }}
    }

    engine = ArenaComfyEngine()
    print('Enviando JSON workflow para o servidor...')
    
    try:
        result = engine.generate.remote(workflow, source_image_b64=img_b64, source_image_name='referencia.jpg')
        
        if result.get('status') == 'success':
            img_data = base64.b64decode(result['image_b64'])
            out_path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_krea2_img2img_puro.jpg'
            with open(out_path, 'wb') as f:
                f.write(img_data)
            print(f'SUCESSO! Imagem salva em: {out_path}')
        else:
            print('Erro no servidor:', result)
            
    except Exception as e:
        print('Erro na execucao:', e)

