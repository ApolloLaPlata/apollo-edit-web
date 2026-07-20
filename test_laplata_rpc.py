import modal
import json
import base64
import os
import time
import sys

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.flux_txt2img_engine import Flux2Txt2ImgEngine

@app.local_entrypoint()
def main():
    print(f"[TEST LAPLATA] Conectando direto via Modal RPC para evitar timeout de 180s do HTTP!")
    
    t0 = time.time()
    print("[TEST LAPLATA] Chamando funcaoo Flux2Txt2ImgEngine.generate...")
    
    engine = Flux2Txt2ImgEngine()
    res = engine.generate.remote(
        prompt="Portrait of Nicolas Maduro in cyberpunk style, highly detailed",
        aspect_ratio="horizontal",
        seed=42
    )

    if res.get("status") == "success":
        b64 = res["image_base64"]
        with open("test_rpc_output.png", "wb") as f:
            f.write(base64.b64decode(b64))
        elapsed = time.time() - t0
        print(f"SUCESSO! Imagem gerada!")
        print(f"Tempo total (Cold Start + Render): {elapsed:.2f}s | Tempo de render na GPU: {res.get('render_time_seconds')}s")
    else:
        print(f"ERRO: {res.get('message')}")
        if res.get("traceback"):
            print(res.get("traceback"))
