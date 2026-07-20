import modal
import base64
import time
import os

input_image_path = r"C:\Users\v5est\Downloads\696191561_122139344121114074_799107263541253788_n.jpg"
prompt = "A personagem Jinx do League of Legends, sentada num sofa confortavelmente, com um gato na perna dela. Corpo inteiro"
out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_modal_output\jinx_pulid.png"
os.makedirs(os.path.dirname(out_path), exist_ok=True)

def main():
    print(f"[TEST JINX] Conectando ao App Deployado via Modal RPC")
    print(f"[TEST JINX] Prompt: {prompt}")

    with open(input_image_path, "rb") as f:
        input_b64 = base64.b64encode(f.read()).decode("utf-8")

    t0 = time.time()
    
    # IMPORTANTE: usando o app DEPLOYADO para aproveitar o snapshot!
    cls = modal.Cls.from_name('apollo-render-router', 'Flux2ComfyEngine_V2')
    
    # Chama o método remoto
    print("Enviando requisição de geração. Como não fizemos snapshot de V2 ainda, isso pode levar 3 mins...")
    
    # We spawn a function call or directly call it:
    try:
        # Pelo que sei do Modal 1.5, methods are accessed like cls().method.remote()
        engine = cls()
        res = engine.generate.remote(
            prompt=prompt,
            aspect_ratio="vertical",
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
            cost = total_time * 0.00160
            
            print(f"\nSUCESSO! Imagem gerada e salva em: {out_path}")
            print(f"Tempo total de execução: {total_time:.2f}s")
            print(f"Tempo de Renderização (GPU): {render_time}s")
            print(f"Tempo de Boot (Cold Start + Rede): {cold_start:.2f}s")
            print(f"Custo total estimado (H100): ${cost:.5f}")
        else:
            print(f"ERRO: {res.get('message')}")
            if res.get("traceback"):
                print(res.get("traceback"))
    except Exception as e:
        print(f"Exception chamando API remota: {e}")

if __name__ == "__main__":
    main()
