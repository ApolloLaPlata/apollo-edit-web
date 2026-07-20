import modal
import base64
import os
import time
import sys

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.flux_engine import Flux2ComfyEngine_V2

input_image_path = r"C:\Users\v5est\Downloads\696191561_122139344121114074_799107263541253788_n.jpg"
prompt = "A personagem Jinx do League of Legends, sentada num sofa confortavelmente, com um gato na perna dela. Corpo inteiro"
out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_modal_output\jinx_pulid.png"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

@app.local_entrypoint()
def main():
    with open(input_image_path, "rb") as f:
        input_b64 = base64.b64encode(f.read()).decode("utf-8")

    print(f"[TEST JINX] Conectando direto via Modal RPC para Img2Img / PuLID")
    print(f"[TEST JINX] Prompt: {prompt}")

    t0 = time.time()
    
    engine = Flux2ComfyEngine_V2()
    # Chama o mtodo remote
    print("Enviando requisio de gerao...")
    res = engine.generate.remote(
        prompt=prompt,
        aspect_ratio="vertical", # ou horizontal, dependendo
        seed=42,
        input_image_b64=input_b64
    )

    t1 = time.time()
    total_time = t1 - t0
    
    if res.get("status") == "success":
        b64 = res["image_base64"]
        img_bytes = base64.b64decode(b64)
        with open(out_path, "wb") as f:
            f.write(img_bytes)
        
        render_time = res.get('render_time_seconds', 0)
        cold_start = total_time - render_time
        
        # Custo da H100 na Modal  $0.00160 por segundo
        cost = total_time * 0.00160
        
        print(f"SUCESSO! Imagem gerada e salva em: {out_path}")
        print(f"Tempo total de execuo: {total_time:.2f}s")
        print(f"Tempo de Renderizao (GPU): {render_time}s")
        print(f"Tempo Estimado de Boot (Cold Start + Rede): {cold_start:.2f}s")
        print(f"Custo total estimado (H100): ${cost:.5f}")
    else:
        print(f"ERRO: {res.get('message')}")
        if res.get("traceback"):
            print(res.get("traceback"))
