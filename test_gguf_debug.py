"""
Teste com debug extenso para capturar os logs do ComfyUI no container.
"""
import modal
import base64
import time
import os
import sys

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.flux_engine import Flux2ComfyEngine_V2

input_image_path = r"C:\Users\v5est\Downloads\696191561_122139344121114074_799107263541253788_n.jpg"
prompt = "Jinx do League of Legends sentada num sofa com um gato na perna, corpo inteiro"
out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_modal_output\jinx_gguf_debug.png"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

@app.local_entrypoint()
def main():
    with open(input_image_path, "rb") as f:
        input_b64 = base64.b64encode(f.read()).decode("utf-8")

    print(f"[LOCAL] Imagem original: {len(input_b64)} chars base64")
    print(f"[LOCAL] Iniciando geracao com DEBUG extenso...")
    
    t0 = time.time()
    engine = Flux2ComfyEngine_V2()
    res = engine.generate.remote(
        prompt=prompt,
        aspect_ratio="vertical",
        seed=12345,
        input_image_b64=input_b64
    )
    t1 = time.time()

    print(f"\n[LOCAL] Resultado: {res.get('status')}")
    print(f"[LOCAL] Engine: {res.get('engine')}")
    print(f"[LOCAL] Tempo total: {t1-t0:.2f}s")
    print(f"[LOCAL] Render time (servidor): {res.get('render_time_seconds')}s")
    
    if res.get("status") == "success":
        img_bytes = base64.b64decode(res["image_base64"])
        with open(out_path, "wb") as f:
            f.write(img_bytes)
        print(f"[LOCAL] Imagem salva: {out_path} ({len(img_bytes)} bytes)")
        
        cost = (t1-t0) * 0.00160
        print(f"[LOCAL] Custo estimado: ${cost:.5f}")
    else:
        print(f"[LOCAL] ERRO: {res.get('message')}")
        if res.get("traceback"):
            print(res.get("traceback"))
