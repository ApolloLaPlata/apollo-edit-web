import sys
try:
    import torch
    from diffusers import LTXPipeline
    from diffusers.utils import export_to_video
    pass
except ImportError:
    pass

def generate_video(prompt: str, output_path: str):
    print(f"Iniciando geracao de video LTX-2 para o prompt: '{prompt}'")
    
    # Carrega pipeline do LTX-Video
    pipe = LTXPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.bfloat16)
    pipe.to("cuda")
    
    # Gera os frames
    video_frames = pipe(
        prompt=prompt,
        width=704,
        height=480,
        num_frames=161,
        num_inference_steps=50,
    ).frames[0]
    
    # Exporta para MP4
    export_to_video(video_frames, output_path, fps=24)
    print(f"Video salvo com sucesso em: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tool_video_gen_ltx.py 'seu prompt aqui' /caminho/output.mp4")
        sys.exit(1)
        
    prompt_arg = sys.argv[1]
    out_arg = sys.argv[2]
    generate_video(prompt_arg, out_arg)
