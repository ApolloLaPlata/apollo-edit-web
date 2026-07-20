import sys
import json
import modal
import os

app = modal.App("converter")

@app.local_entrypoint()
def main():
    ui_path = r"H:\COMFYUI\WORKFLOW\WORKFLOWS\WORKFLOW - INSANE UPSCALE\WORKFLOW - INSANE UPSCALE.json"
    with open(ui_path, "r", encoding="utf-8") as f:
        ui_json_string = f.read()
        
    print(f"Enviando {len(ui_json_string)} bytes para a nuvem para conversao...")
    
    # Lookup the class on Modal
    engine_cls = modal.Cls.from_name("apollo-render-router", "UniversalComfyEngine")
    engine = engine_cls()
    result = engine.convert_ui_to_api.remote(ui_json_string)
    
    if result.get("status") == "success":
        api_json = result["api_json"]
        if "data" in api_json and "prompt" in api_json["data"]:
            api_json = api_json["data"]["prompt"]
            
        out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\WORKFLOW - INSANE UPSCALE\WORKFLOW - INSANE UPSCALE.json"
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(api_json, f, indent=4)
        print(f"Sucesso! Salvo em {out_path}")
    else:
        print("Erro na conversao:")
        print(result)
