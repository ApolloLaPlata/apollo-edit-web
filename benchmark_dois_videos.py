import modal
import os
import torch
import time

app = modal.App("benchmark-dois-videos")
vol = modal.Volume.from_name("apollo-models-vol")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "git")
    .pip_install(
        "torch", "torchvision", "torchaudio",
        "git+https://github.com/huggingface/diffusers.git", "git+https://github.com/huggingface/transformers.git", "accelerate",
        "huggingface_hub", "sentencepiece", "safetensors",
        "peft", "scipy", "av", "moviepy"
    )
)

@app.function(gpu="H100", image=image, volumes={"/models": vol}, timeout=1200)
def generate_two_videos():
    from diffusers import LTX2Pipeline
    from diffusers.utils import export_to_video
    from diffusers.pipelines.ltx2.export_utils import encode_video
    
    results = []
    
    print("Carregando pipeline (iniciando o motor)...")
    start_load = time.time()
    cache_dir = "/models/huggingface/hub/models--diffusers--LTX-2.3-Diffusers"
    pipe = LTX2Pipeline.from_pretrained(
        cache_dir,
        torch_dtype=torch.bfloat16,
        local_files_only=True
    )
    pipe.to("cuda")
    load_time = time.time() - start_load
    print(f"Pipeline carregado em {load_time:.2f} segundos.")
    
    # --- Video 1 ---
    print("\n--- Gerando VÍDEO 1 (Motor recém-ligado) ---")
    start_vid1 = time.time()
    prompt1 = "A realistic brazilian reporter holding a microphone, speaking to the camera in portuguese saying 'Boa noite, estas são as principais notícias do dia'. Urban city background, 4k, hyperrealistic"
    negative_prompt = "worst quality, inconsistent, blurry, deformed, plastic, doll, 3d render, cg, fake, painting"
    
    output1 = pipe(
        prompt=prompt1,
        negative_prompt=negative_prompt,
        width=854,
        height=480,
        num_frames=121,
        num_inference_steps=25
    )
    
    video1 = output1.frames[0]
    audio1 = output1.audio
    
    audio_sample_rate = 48000
    if hasattr(pipe, "vocoder") and hasattr(pipe.vocoder, "config"):
        audio_sample_rate = pipe.vocoder.config.output_sampling_rate
        
    out_path1 = "/tmp/video1.mp4"
    if audio1 is not None and len(audio1) > 0 and audio1[0] is not None:
        encode_video(
            video1,
            fps=24,
            audio=audio1[0].float().cpu() if hasattr(audio1[0], "float") else audio1[0],
            audio_sample_rate=audio_sample_rate,
            output_path=out_path1,
        )
    else:
        export_to_video(video1, out_path1, fps=24)
        
    time_vid1 = time.time() - start_vid1
    print(f"Vídeo 1 gerado e encodado em {time_vid1:.2f} segundos.")
    with open(out_path1, "rb") as f:
        vid1_bytes = f.read()
    
    # --- Video 2 ---
    print("\n--- Gerando VÍDEO 2 (Motor já quente) ---")
    start_vid2 = time.time()
    prompt2 = "A realistic brazilian reporter holding a microphone, speaking to the camera in portuguese saying 'Agora vamos para a previsão do tempo de amanhã'. Urban city background, 4k, hyperrealistic"
    
    output2 = pipe(
        prompt=prompt2,
        negative_prompt=negative_prompt,
        width=854,
        height=480,
        num_frames=121,
        num_inference_steps=25
    )
    
    video2 = output2.frames[0]
    audio2 = output2.audio
        
    out_path2 = "/tmp/video2.mp4"
    if audio2 is not None and len(audio2) > 0 and audio2[0] is not None:
        encode_video(
            video2,
            fps=24,
            audio=audio2[0].float().cpu() if hasattr(audio2[0], "float") else audio2[0],
            audio_sample_rate=audio_sample_rate,
            output_path=out_path2,
        )
    else:
        export_to_video(video2, out_path2, fps=24)
        
    time_vid2 = time.time() - start_vid2
    print(f"Vídeo 2 gerado e encodado em {time_vid2:.2f} segundos.")
    with open(out_path2, "rb") as f:
        vid2_bytes = f.read()
        
    return {
        "load_time": load_time,
        "time_vid1": time_vid1,
        "time_vid2": time_vid2,
        "vid1_bytes": vid1_bytes,
        "vid2_bytes": vid2_bytes
    }

@app.local_entrypoint()
def main():
    print("Iniciando benchmark de geração sequencial na nuvem Modal (H100)...")
    t0 = time.time()
    res = generate_two_videos.remote()
    t1 = time.time()
    total_time = t1 - t0
    
    print("\n================ RELATÓRIO DE TEMPOS ================")
    print(f"Tempo de carga do modelo na VRAM: {res['load_time']:.2f}s")
    print(f"Tempo de geração Vídeo 1 (quente + inferência): {res['time_vid1']:.2f}s")
    print(f"Tempo de geração Vídeo 2 (quente): {res['time_vid2']:.2f}s")
    print(f"Tempo total (incluindo overhead de rede Modal): {total_time:.2f}s")
    
    # Custo de H100 no Modal é ~$4.30 por hora -> ~$0.00119 por segundo
    custo_por_segundo = 0.00119
    custo_total = total_time * custo_por_segundo
    
    print("\n================ RELATÓRIO DE CUSTOS ================")
    print(f"Custo estimado total desta rodada na H100: ${custo_total:.4f} USD")
    
    pasta_destino = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_todos_modelos"
    os.makedirs(pasta_destino, exist_ok=True)
    
    out1 = os.path.join(pasta_destino, "novo_ltx_video1_ptbr.mp4")
    out2 = os.path.join(pasta_destino, "novo_ltx_video2_ptbr.mp4")
    
    with open(out1, "wb") as f:
        f.write(res["vid1_bytes"])
    with open(out2, "wb") as f:
        f.write(res["vid2_bytes"])
        
    print(f"\nVídeos salvos com SUCESSO em:")
    print(f"1: {out1}")
    print(f"2: {out2}")
