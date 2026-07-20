import json

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/image_flux2/image_flux2_pulid_dynamic.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

# Fix DualCLIPLoader
wf['98:38']['class_type'] = 'DualCLIPLoader'
wf['98:38']['inputs'] = {
    'clip_name1': 't5xxl_fp16.safetensors',
    'clip_name2': 'clip_l.safetensors',
    'type': 'flux'
}

# Fix UNET
wf['98:12']['inputs']['unet_name'] = 'flux1-dev.safetensors'

# Fix VAE
wf['98:10']['inputs']['vae_name'] = 'ae.safetensors'

# Remove Lora Loader and Model Switch completely
if '98:101' in wf: del wf['98:101']
if '98:102' in wf: del wf['98:102']

# Point Pulid model directly to UNET
wf['1004']['inputs']['model'] = ['98:12', 0]

# Add Redux nodes
wf['1006'] = {
    'class_type': 'StyleModelLoader',
    'inputs': { 'style_model_name': 'flux1-redux-dev.safetensors' }
}
wf['1007'] = {
    'class_type': 'CLIPVisionLoader',
    'inputs': { 'clip_name': 'sigclip_vision_patch14_384.safetensors' }
}
wf['1008'] = {
    'class_type': 'CLIPVisionEncode',
    'inputs': {
        'clip_vision': ['1007', 0],
        'image': ['1005', 0],
        'crop': 'center'
    }
}
wf['1009'] = {
    'class_type': 'StyleModelApply',
    'inputs': {
        'conditioning': ['98:26', 0],
        'style_model': ['1006', 0],
        'clip_vision_output': ['1008', 0],
        'strength': 1.0,
        'strength_type': 'multiply'
    }
}

# Rewire BasicGuider to take from StyleModelApply
wf['98:22']['inputs']['conditioning'] = ['1009', 0]

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/image_flux2/image_flux2_pulid_redux.json', 'w', encoding='utf-8') as f:
    json.dump(wf, f, indent=2)

print('JSON corrigido perfeitamente sem quebrar o booleano 98:104!')
