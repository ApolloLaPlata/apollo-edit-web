import sys
try:
    import torch
    from diffusers import FluxPipeline
    pass
except ImportError:
    pass

def generate_image(prompt: str, output_path: str):
    print(f"Iniciando geracao de imagem para o prompt: '{prompt}'")
    
    # Baixa o modelo direto para VRAM (bfloat16 para economizar memoria)
    pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload() # Otimizacao para GPUs menores como a L4
    
    # Gera a imagem (Schnell precisa de poucos steps, ex: 4)
    image = pipe(
        prompt,
        guidance_scale=0.0,
        num_inference_steps=4,
        max_sequence_length=256,
    ).images[0]
    
    image.save(output_path)
    print(f"Imagem salva com sucesso em: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_image_gen_flux.py 'seu prompt aqui' /caminho/output.png")
        sys.exit(1)
        
    prompt_arg = sys.argv[1]
    out_arg = sys.argv[2]
    generate_image(prompt_arg, out_arg)
