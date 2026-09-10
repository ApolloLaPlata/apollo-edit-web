import json
import base64
import os
import io
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_krea2_pulid_modal():
    print('Iniciando Runtime Patch do PuLID...')
    import os, re
    hook_path = '/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/PulidFluxHook.py'
    if os.path.exists(hook_path):
        c = open(hook_path, 'r').read()
        # Desfazendo a burrada de trocar forward_orig por forward
        c = c.replace('def pulid_forward(self,', 'def pulid_forward_orig(self,')
        c = c.replace('out = self.forward(img', 'out = self.forward_orig(img')
        c = c.replace('def pulid_forward_orig(self, *args, **kwargs):', 'def pulid_forward_orig(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None, **kwargs):')
        c = re.sub(r'def pulid_forward_orig\(self, img: Tensor, img_ids: Tensor, txt: Tensor, txt_ids: Tensor, timesteps: Tensor, y: Tensor, guidance: Tensor = None, control = None, transformer_options=\{\}, attn_mask: Tensor = None, \*\*kwargs\) -> Tensor:', 'def pulid_forward_orig(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None, **kwargs):', c)
        open(hook_path, 'w').write(c)

    main_path = '/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py'
    if os.path.exists(main_path):
        c2 = open(main_path, 'r').read()
        c2 = c2.replace('m.forward = pulid_forward.__get__(m, type(m))', 'm.forward_orig = pulid_forward_orig.__get__(m, type(m))')
        open(main_path, 'w').write(c2)
    print('PuLID Runtime Patch Aplicado com Sucesso!')
    print('Iniciando Runtime Patch do PuLID...')
    import os, re
    hook_path = '/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/PulidFluxHook.py'
    if os.path.exists(hook_path):
        c = open(hook_path, 'r').read()
        # Restaurar a assinatura original que o Python espera quando kwargs sao ignorados
        c = re.sub(r'def pulid_forward\(self, img: Tensor, img_ids: Tensor, txt: Tensor, txt_ids: Tensor, timesteps: Tensor, y: Tensor, guidance: Tensor = None, control = None, transformer_options={}, attn_mask: Tensor = None, \*\*kwargs\) -> Tensor:', 'def pulid_forward(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None, **kwargs):', c)
        c = c.replace('def pulid_forward(self, *args, **kwargs):', 'def pulid_forward(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None, **kwargs):')
        open(hook_path, 'w').write(c)
        print('PuLID Runtime Patch Aplicado com Sucesso!')
    print("Iniciando teste Krea-2-Raw com PuLID (Zero-Shot Character Insertion)...")
    
    img_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char2_turnaround.png"
    with open(img_path, "rb") as f:
        input_data = f.read()
    
    img_b64 = base64.b64encode(input_data).decode("utf-8")
    
    # Workflow Krea-2-Raw + PuLID (Text-to-Image with Character Prompt)
    workflow = {
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "A cinematic photo of a blonde man wearing a dark blue suit and a red tie, sitting alone at a rustic bar counter, drinking a glass of beer, highly detailed, realistic, facing the camera",
                "clip": ["11", 0]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["13", 0],
                "vae": ["10", 0]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "pulid_turnaround_test",
                "images": ["8", 0]
            }
        },
        "10": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors"
            }
        },
        "11": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "t5xxl_fp16.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux"
            }
        },
        "12": {
            "class_type": "UNETLoader",
            "inputs": {
                "weight_dtype": "default",
                "unet_name": "redzibDX1.safetensors"
            }
        },
        "13": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["25", 0],
                "guider": ["22", 0],
                "sampler": ["16", 0],
                "sigmas": ["17", 0],
                "latent_image": ["27", 0]
            }
        },
        "16": {
            "class_type": "KSamplerSelect",
            "inputs": {
                "sampler_name": "euler"
            }
        },
        "17": {
            "class_type": "BasicScheduler",
            "inputs": {
                "scheduler": "simple",
                "steps": 25,
                "denoise": 1,
                "model": ["36", 0]
            }
        },
        "22": {
            "class_type": "BasicGuider",
            "inputs": {
                "model": ["36", 0],
                "conditioning": ["6", 0]
            }
        },
        "25": {
            "class_type": "RandomNoise",
            "inputs": {
                "noise_seed": 777
            }
        },
        "27": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            }
        },
        "30": {
            "class_type": "PulidFluxModelLoader",
            "inputs": {
                "pulid_file": "pulid_flux_v0.9.0.safetensors"
            }
        },
        "31": {
            "class_type": "PulidFluxInsightFaceLoader",
            "inputs": {
                "provider": "CPU"
            }
        },
        "32": {
            "class_type": "PulidFluxEvaClipLoader",
            "inputs": {}
        },
        "35": {
            "class_type": "LoadImage",
            "inputs": {
                "image": "referencia.png",
                "upload": "image"
            }
        },
        "36": {
            "class_type": "ApplyPulidFlux",
            "inputs": {
                "weight": 1.0,
                "start_at": 0,
                "end_at": 1,
                "model": ["12", 0],
                "pulid_flux": ["30", 0],
                "eva_clip": ["32", 0],
                "face_analysis": ["31", 0],
                "image": ["35", 0]
            }
        }
    }

    engine = ArenaComfyEngine()
    
    print("Enviando JSON workflow para o servidor Modal Krea-2-Raw + PuLID...")
    
    try:
        result = engine.generate.remote(workflow, source_image_b64=img_b64, source_image_name="referencia.png")
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_krea2_pulid.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor:", result)
            
    except Exception as e:
        print("Erro na execucao:", e)


