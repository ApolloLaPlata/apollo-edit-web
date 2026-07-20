import json
import base64
import urllib.request
import time
import os

def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def main():
    print("Iniciando Teste Multi-Pass via Cloud Modal...")
    
    workflow_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\FLUX 2 DEV\image_flux2\workflow_multipass_pulid.json"
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_json_string = f.read()
        
    jinx_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_modal_output\elon_musk_sorvete_txt2img.png"
    
    if not os.path.exists(jinx_path):
        print("Imagem da Jinx não encontrada, usando dummy.")
        jinx_b64 = "" # We could generate a dummy or just use it if it exists
    else:
        jinx_b64 = image_to_base64(jinx_path)
        
    import json
    with open("Comfyui Workflow API/WORKFLOW - INSANE UPSCALE/WORKFLOW - INSANE UPSCALE.json", "r", encoding="utf-8") as f:
        upscale_wf = json.load(f)
        
    for node_id, node in upscale_wf.items():
        if node.get("class_type") == "UNETLoader" and "unet_name" in node.get("inputs", {}):
            node["inputs"]["unet_name"] = "flux1-dev-fp8.safetensors"
        if node.get("class_type") == "LoadImage":
            if "_meta" not in node:
                node["_meta"] = {}
            node["_meta"]["title"] = "APOLLO_BASE_IMAGE"
            
    upscale_wf_str = json.dumps(upscale_wf)
    
    script = {
        "workflow_json_string": workflow_json_string,
        "etapas": [
            {
                "prompt": "Portrait of Elon Musk wearing a casual black polo shirt, eating an ice cream cone in a neon lit cyberpunk city at night. ultra detailed skin pores, sharp focus, 8k resolution, raw DSLR photography, cinematic lighting, photorealistic, highly detailed face",
                "image_b64": jinx_b64
            },
            {
                "prompt": "Portrait of Elon Musk wearing a casual black polo shirt, eating an ice cream cone in a neon lit cyberpunk city at night. ultra detailed skin pores, sharp focus, 8k resolution, raw DSLR photography, cinematic lighting, photorealistic, highly detailed face",
                "image_b64": jinx_b64
            },
            {
                "prompt": "Portrait of Elon Musk wearing a casual black polo shirt, eating an ice cream cone in a neon lit cyberpunk city at night. ultra detailed skin pores, sharp focus, 8k resolution, raw DSLR photography, cinematic lighting, photorealistic, highly detailed face",
                "image_b64": jinx_b64,
                "workflow_json_string": upscale_wf_str
            }
        ]
    }
    
    payload = json.dumps({"script": script}).encode("utf-8")
    
    url = "https://historiasde7dias--apollo-render-router-apollo-api.modal.run/multi_pass"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    t0 = time.time()
    try:
        print("Enviando request para o webhook do Modal...")
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode("utf-8"))
        
        print(f"Status: {result.get('status')}")
        if result.get('status') == 'success':
            img_b64 = result.get('image_base64')
            out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_modal_output\resultado_multipass_api_test.png"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            print(f"Imagem salva com sucesso em {out_path}")
            print(f"Tempo total: {time.time() - t0:.2f}s")
        else:
            print("ERRO:", result.get('message'))
            
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    main()
