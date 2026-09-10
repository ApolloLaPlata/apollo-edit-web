
import modal
import base64

def run():
    print("Iniciando teste T2I diretamente no Modal...")
    cls = modal.Cls.from_name("apollo-render-router", "QwenImageEngine")
    engine = cls()
    prompt = "A highly detailed cinematic shot of a futuristic cyberpunk hacker coding in a neon-lit room, 8k resolution, photorealistic"
    
    print("Aguardando geracao...")
    result = engine.generate.remote(prompt=prompt, images_b64=[], aspect_ratio="horizontal")
    
    if result.get("status") == "success":
        b64 = result["image_b64"]
        with open("qwen_t2i_test_result.jpg", "wb") as img:
            img.write(base64.b64decode(b64))
        print("SUCESSO: qwen_t2i_test_result.jpg salvo!")
    else:
        print("ERRO:", result)

if __name__ == "__main__":
    run()

