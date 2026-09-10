import modal
import time
import base64

def test_rpc():
    print("Conectando a Modal via RPC (sem limite de 180s)...")
    try:
        # Pelo novo SDK da Modal, o lookup de métodos de uma classe é feito via Function:
        f = modal.Function.lookup("apollo-render-router", "Flux2Txt2ImgEngine.generate")
        
        print("Disparando engine.generate()... O Cold Start de Snapshot pode levar de 2 a 3 mins na 1a vez...")
        t0 = time.time()
        
        res = f.remote(
            prompt="Portrait of Nicolas Maduro in cyberpunk style, highly detailed",
            aspect_ratio="horizontal",
            seed=42
        )
        t1 = time.time()
        
        print(f"Sucesso! Tempo total (RPC): {t1 - t0:.2f}s")
        if res.get("status") == "success":
            print("Render time interno:", res.get("render_time_seconds", "N/A"))
            b64 = res.get("image_base64", "")
            if b64:
                with open("test_rpc_output.png", "wb") as f:
                    f.write(base64.b64decode(b64))
                print("Imagem salva como test_rpc_output.png")
        else:
            print("Resultado:", res)
            
    except Exception as e:
        print(f"Erro no RPC: {e}")

if __name__ == "__main__":
    test_rpc()
