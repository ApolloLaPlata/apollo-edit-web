import modal
import os
import urllib.request
import json
import time
import base64
import uuid

import backend.cloud_tools.modal_app as app_module
from backend.cloud_tools.modal_app import app

# Lemos um arquivo local para quebrar o cache do Docker (Update System)
try:
    with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/comfy_update_timestamp.txt", "r") as f:
        cache_buster = f.read().strip()
except Exception:
    cache_buster = "initial"

from backend.cloud_tools.engines.flux_engine import flux2_comfy_image
comfy_universal_image = flux2_comfy_image

@app.cls(gpu="h100", timeout=1200, image=comfy_universal_image, scaledown_window=600)
class UniversalComfyEngine:
    @modal.enter()
    def start_server(self):
        import subprocess
        import time
        import urllib.request
        
        print("[UniversalComfyEngine] Iniciando servidor ComfyUI headless...")
        subprocess.check_call(["pip", "install", "websocket-client"])
        self.log_file = open("/tmp/comfy_log.txt", "w")
        self.server_process = subprocess.Popen(
            ["python", "main.py", "--listen", "127.0.0.1", "--port", "8188"],
            cwd="/comfyui",
            stdout=self.log_file,
            stderr=subprocess.STDOUT
        )
        
        for i in range(30):
            try:
                urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=2)
                print("[UniversalComfyEngine] Servidor online!")
                break
            except:
                time.sleep(2)
        else:
            print("[UniversalComfyEngine] FALHA AO INICIAR! Logs:")
            with open("/tmp/comfy_log.txt", "r") as f:
                print(f.read())

    @modal.method()
    def generate(self, workflow: dict, input_node_id: str, input_value: str, output_node_id: str, reference_images_base64: list[str] = None):
        import urllib.request
        import json
        import time
        import websocket
        import os
        import base64
        import random
        
        t0 = time.time()
        client_id = str(uuid.uuid4())
        
        # Mapeamento do Input Principal de Texto
        if input_node_id and input_node_id in workflow:
            if "text" in workflow[input_node_id]["inputs"]:
                workflow[input_node_id]["inputs"]["text"] = input_value
            elif "string" in workflow[input_node_id]["inputs"]:
                workflow[input_node_id]["inputs"]["string"] = input_value
                
        # Tratamento de Imagens de Referencia (LoadImage)
        if reference_images_base64 and len(reference_images_base64) > 0:
            b64_data = reference_images_base64[0]
            if b64_data:
                if "," in b64_data:
                    b64_data = b64_data.split(",")[1]
                
                # Fix Incorrect padding
                b64_data += "=" * ((4 - len(b64_data) % 4) % 4)
                
                print(f"[UniversalComfyEngine] Base64 string length before decode: {len(b64_data)}")
                try:
                    img_data = base64.b64decode(b64_data, validate=True)
                except Exception as e:
                    print(f"[UniversalComfyEngine] Base64 Decode falhou! Primeira 50 char: {b64_data[:50]}")
                    raise e
                
                filename = f"apollo_input_{client_id}.png"
                input_dir = "/comfyui/input"
                os.makedirs(input_dir, exist_ok=True)
                with open(os.path.join(input_dir, filename), "wb") as f:
                    f.write(img_data)
                
                # Procura o no LoadImage que usamos no Flux2 (geralmente id 46 ou similar passado via dict)
                # Como o usuario mandou image_flux2.json, sabemos que o no de imagem e 46
                # Vamos buscar dinamicamente pelo tipo LoadImage se nao soubermos
                for n_id, n_data in workflow.items():
                    if n_data.get("class_type") == "LoadImage":
                        n_data["inputs"]["image"] = filename
                
        for node_id, node_data in workflow.items():
            if "inputs" in node_data:
                for k in list(node_data["inputs"].keys()):
                    if "seed" in k.lower():
                        node_data["inputs"][k] = random.randint(1, 9999999999)
                        
        p = {"prompt": workflow, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        
        print(f"[UniversalComfyEngine] Conectando ao Websocket para streaming de logs...")
        ws = websocket.WebSocket()
        ws.connect(f"ws://127.0.0.1:8188/ws?clientId={client_id}")
        
        req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            prompt_id = result['prompt_id']
            
        yield {"type": "log", "message": f"Job iniciado (ID: {prompt_id})"}
        
        while True:
            out = ws.recv()
            if isinstance(out, str):
                msg = json.loads(out)
                if msg['type'] == 'progress':
                    val = msg['data']['value']
                    max_val = msg['data']['max']
                    yield {"type": "log", "message": f"Processando: {val}/{max_val} passos"}
                elif msg['type'] == 'executing':
                    node = msg['data']['node']
                    if node is None:
                        yield {"type": "log", "message": f"Pipeline finalizado! Extraindo resultado..."}
                        break
                    yield {"type": "log", "message": f"Executando no: {node}"}
                elif msg['type'] == 'execution_error':
                    yield {"type": "error", "message": f"Erro no ComfyUI: {msg['data']}"}
                    break

        ws.close()
        
        req_hist = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
        with urllib.request.urlopen(req_hist) as res:
            hist = json.loads(res.read())
            
        if prompt_id in hist:
            outputs = hist[prompt_id]['outputs']
            if output_node_id in outputs and 'images' in outputs[output_node_id]:
                img_info = outputs[output_node_id]['images'][0]
                filename = img_info['filename']
                subfolder = img_info.get('subfolder', '')
                
                img_path = os.path.join("/comfyui/output", subfolder, filename)
                with open(img_path, "rb") as f:
                    img_bytes = f.read()
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                
                render_time = time.time() - t0
                yield {
                    "type": "result",
                    "status": "success",
                    "image_base64": b64,
                    "render_time_seconds": round(render_time, 2)
                }
            else:
                yield {"type": "error", "message": f"Nó de output {output_node_id} não gerou imagens."}
        else:
            yield {"type": "error", "message": "Histórico não encontrado."}
