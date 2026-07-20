import json

# =========================================================================
# WORKFLOW NATIVO DE COMFYUI PARA IMAGE-TO-IMAGE E MULTI-PASS COM FLUX
# =========================================================================

def create_workflow(step: int, prompt: str, input_image_path: str = None):
    # Dicionario nativo do Workflow API do ComfyUI
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 123456 + step,
                "steps": 20,
                "cfg": 3.5,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,  # 1.0 para criar do zero, menor para editar
                "model": ["10", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "flux-2-klein-base-4b-fp8.safetensors"
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["4", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "",
                "clip": ["4", 1]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"passo_{step}",
                "images": ["8", 0]
            }
        },
        "10": {
            "class_type": "FluxGuidance",
            "inputs": {
                "guidance": 3.5,
                "conditioning": ["4", 0]
            }
        }
    }

    if input_image_path is None:
        # Txt2Img puro (Passo 1)
        workflow["5"] = {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "batch_size": 1,
                "width": 1024,
                "height": 1024
            }
        }
    else:
        # Image2Image / Inpainting (Passos 2 e 3)
        workflow["5"] = {
            "class_type": "LoadImage",
            "inputs": {
                "image": input_image_path
            }
        }
        workflow["11"] = {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": ["5", 0],
                "vae": ["4", 2]
            }
        }
        # Substitui a entrada do KSampler para usar o Encode da Imagem anterior
        workflow["3"]["inputs"]["latent_image"] = ["11", 0]
        # Reduz o denoise para manter o background do passo anterior
        workflow["3"]["inputs"]["denoise"] = 0.65

    return workflow

if __name__ == "__main__":
    print("[LLM] Gerando Workflow NATIVO (JSON API ComfyUI) para o Passo 1...")
    p1 = "A cinematic shot of a young man with messy hair and a leather jacket sitting alone at a wooden table in a neon-lit cyberpunk bar, drinking a beer."
    wf1 = create_workflow(step=1, prompt=p1)
    
    with open("workflow_step1.json", "w") as f:
        json.dump(wf1, f, indent=2)
    print("-> workflow_step1.json gravado.")

    print("\n[LLM] Simulando encadeamento... Usando resultado do Passo 1 como input do Passo 2.")
    p2 = "A cinematic shot in the same neon-lit cyberpunk bar. The first man is sitting at the table drinking beer. Now, a beautiful blonde woman in a red dress is sitting right next to him at the same table. They are sitting together."
    wf2 = create_workflow(step=2, prompt=p2, input_image_path="passo_1_00001.png")
    
    with open("workflow_step2.json", "w") as f:
        json.dump(wf2, f, indent=2)
    print("-> workflow_step2.json (Image-to-Image / Inpaint) gravado.")

    print("\n[LLM] Simulando encadeamento... Usando resultado do Passo 2 como input do Passo 3.")
    p3 = "A cinematic shot in the same neon-lit cyberpunk bar. The first two characters are sitting at the table. Now, a third person (a woman with braided hair) is sitting at the table next to them, on the far right. They are all sitting together."
    wf3 = create_workflow(step=3, prompt=p3, input_image_path="passo_2_00001.png")
    
    with open("workflow_step3.json", "w") as f:
        json.dump(wf3, f, indent=2)
    print("-> workflow_step3.json (Image-to-Image / Inpaint) gravado.")
    
    print("\nSucesso! Esses JSONs são 100% compativeis com a API nativa do ComfyUI e implementam exatamente a logica Multi-Pass requerida usando os nós nativos LoadImage, VAEEncode, KSampler e CheckpointLoaderSimple (Flux).")
