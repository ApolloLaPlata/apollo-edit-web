import modal
import json
import base64
import os
import time
import sys

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.flux_engine import Flux2ComfyEngine

out_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_modal_output"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "homem_paraquedas.png")

prompt = "homem pulando de paraquedas no ceu noturno cheio de estrelas brilhantes"
input_image_path = r"C:\Users\v5est\Downloads\Gemini_Generated_Image_1xmgbi1xmgbi1xmg.png"

@app.local_entrypoint()
def main():
    with open(input_image_path, "rb") as f:
        input_b64 = base64.b64encode(f.read()).decode("utf-8")

    print(f"[TEST FLUX 2] Conectando direto via Modal RPC para evitar timeout de 180s do HTTP!")
    print(f"[TEST FLUX 2] Prompt: {prompt}")

    t0 = time.time()
    print("[TEST FLUX 2] Chamando função. Isso pode levar alguns minutos em cold start (até 6 min). Aguarde...")
    
    import random
    seed = random.randint(1, 9999999)

    engine = Flux2ComfyEngine()
    res = engine.generate.remote(
        prompt=prompt,
        aspect_ratio="horizontal",
        seed=seed,
        input_image_b64=input_b64
    )

    if res.get("status") == "success":
        b64 = res["image_base64"]
        img_bytes = base64.b64decode(b64)
        with open(out_path, "wb") as f:
            f.write(img_bytes)
        elapsed = time.time() - t0
        print(f"✅ SUCESSO! Imagem gerada e salva em: {out_path}")
        print(f"⏱️ Tempo total: {elapsed:.2f}s | Tempo de render na A100: {res.get('render_time_seconds')}s")
    else:
        print(f"❌ ERRO: {res.get('message')}")
        if res.get("traceback"):
            print(res.get("traceback"))


