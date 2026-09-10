import json
import base64
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_omnigen_modal():
    print("Iniciando Teste do OmniGen (Base) na Arena...")
    
    # Workflow OmniGen
    workflow = {
        "1": { 
            "class_type": "LoadImage", 
            "inputs": { "image": "referencia_bombadao.jpg" }
        },
        "2": { 
            "class_type": "ailab_OmniGen", 
            "inputs": { 
                "preset_prompt": "None",
                "prompt": "A cinematic photo of the muscular man in <img>image_1</img> wearing a black beanie and punisher tank top, riding a mountain bike on a sunny beach boardwalk",
                "model_precision": "FP16",
                "memory_management": "Speed Priority",
                "guidance_scale": 2.5,
                "img_guidance_scale": 1.4,
                "num_inference_steps": 50,
                "separate_cfg_infer": True,
                "use_input_image_size_as_output": False,
                "width": 1024,
                "height": 1024,
                "seed": 999,
                "max_input_image_size": 1024,
                "image_1": ["1", 0]
            }
        },
        "3": { 
            "class_type": "SaveImage", 
            "inputs": { "images": ["2", 0], "filename_prefix": "omnigen_result" }
        }
    }

    engine = ArenaComfyEngine()
    
    # Send the reference image
    img_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/referencia_bombadao.jpg"
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    print("Enviando JSON workflow para o servidor Modal...")
    
    try:
        result = engine.generate.remote(workflow, source_image_b64=img_b64, source_image_name="referencia_bombadao.jpg")
        
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

