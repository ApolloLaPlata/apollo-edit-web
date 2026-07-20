import modal
import os
import torch
import scipy.io.wavfile

app = modal.App("ltx-manual-generator")

vol = modal.Volume.from_name("apollo-models-vol")

image = modal.Image.debian_slim(python_version="3.10").pip_install(
    "diffusers", "transformers", "accelerate", "scipy", "sentencepiece", "peft"
)

@app.function(gpu="H100", image=image, volumes={"/models": vol}, timeout=1200)
def generate_video():
    from diffusers import LTX2Pipeline
    from diffusers.utils import export_to_video, encode_video
    
    print("Loading pipeline...")
    cache_dir = "/models/huggingface/hub/models--diffusers--LTX-2.3-Diffusers"
    pipe = LTX2Pipeline.from_pretrained(
        cache_dir,
        torch_dtype=torch.bfloat16,
        local_files_only=True
    )
    pipe.to("cuda")
    
    print("Pipeline loaded. Generating video...")
    prompt = "A realistic brazilian reporter holding a microphone, speaking to the camera in portuguese saying 'Boa noite, estas são as principais notícias do dia'. Urban city background, 4k, hyperrealistic"
    negative_prompt = "worst quality, inconsistent, blurry, deformed, plastic, doll, 3d render, cg, fake, painting"
    
    output = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=854,
        height=480,
        num_frames=121,
        num_inference_steps=25,
        decode_chunk_size=4
    )
    
    video = output.frames[0]
    audio = output.audio
    
    print("Encoding video...")
    audio_sample_rate = 48000
    if hasattr(pipe, "vocoder") and hasattr(pipe.vocoder, "config"):
        audio_sample_rate = pipe.vocoder.config.output_sampling_rate
        
    out_path = "/tmp/output.mp4"
    if audio is not None and len(audio) > 0 and audio[0] is not None:
        encode_video(
            video,
            fps=24,
            audio=audio[0].float().cpu() if hasattr(audio[0], "float") else audio[0],
            audio_sample_rate=audio_sample_rate,
            output_path=out_path,
        )
    else:
        export_to_video(video, out_path, fps=24)
        
    with open(out_path, "rb") as f:
        video_bytes = f.read()
        
    return video_bytes

@app.local_entrypoint()
def main():
    print("Disparando geração...")
    video_bytes = generate_video.remote()
    out_file = r"C:\Users\v5est\.gemini\antigravity\brain\0e14241d-91af-4860-8795-5ae227d39bc9\modal_ltx_output.mp4"
    with open(out_file, "wb") as f:
        f.write(video_bytes)
    print(f"Vídeo salvo em {out_file}")
