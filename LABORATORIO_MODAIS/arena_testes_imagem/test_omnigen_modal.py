import json
import base64
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_omnigen_modal():
    print("Iniciando Teste do OmniGen (Base) na Arena...")
    
    # Workflow OmniGen (Multi-Character Test)
    workflow = {
        "1": { 
            "class_type": "LoadImage", 
            "inputs": { "image": "char1.png" }
        },
        "1_2": { 
            "class_type": "LoadImage", 
            "inputs": { "image": "char2.png" }
        },
        "1_3": { 
            "class_type": "LoadImage", 
            "inputs": { "image": "char3.png" }
        },
        "2": { 
            "class_type": "ailab_OmniGen", 
            "inputs": {
                "preset_prompt": "None",
                "memory_management": "Speed Priority",
                "model_precision": "FP16",
                "prompt": "A 2D cartoon flat illustration in the exact same art style, small proportions, and aesthetic as the reference images. The three men image_1, image_2, and image_3 are sitting together behind a news anchor desk in a television studio, highly detailed.",
                "num_inference_steps": 50,
                "guidance_scale": 3.0,
                "img_guidance_scale": 1.6,
                "max_input_image_size": 1024,
                "separate_cfg_infer": True,
                "offload_model": False,
                "use_input_image_size_as_output": False,
                "width": 1024,
                "height": 1024,
                "seed": 8888,
                "image_1": ["1", 0],
                "image_2": ["1_2", 0],
                "image_3": ["1_3", 0]
            }
        },
        "3": { 
            "class_type": "SaveImage", 
            "inputs": { "images": ["2", 0], "filename_prefix": "omnigen_multichar" }
        }
    }

    engine = ArenaComfyEngine()
    
    # Load the 3 reference images
    def load_b64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
            
    img1_b64 = load_b64("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char1_turnaround.png")
    img2_b64 = load_b64("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char2_turnaround.png")
    img3_b64 = load_b64("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char3_turnaround.png")
        
    print("Enviando JSON workflow para o servidor Modal (Multi-Character)...")
    
    try:
        images_dict = {
            "char1.png": img1_b64,
            "char2.png": img2_b64,
            "char3.png": img3_b64
        }
        result = engine.generate.remote(workflow, multiple_images=images_dict)
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_omnigen.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor:", result)
            
    except Exception as e:
        print("Erro na execucao:", e)
