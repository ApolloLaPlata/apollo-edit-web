import modal
import os
import io
import base64
import traceback
import time

app = modal.App("apollo-render-router")

# ─── Imagem do ambiente ────────────────────────────────────────────────────────
apollo_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "git")
    .pip_install(
        "requests", "fastapi", "pydantic",
        "torch", "torchvision", "torchaudio",
        "git+https://github.com/huggingface/diffusers.git", "git+https://github.com/huggingface/transformers.git", "accelerate",
        "huggingface_hub", "sentencepiece", "tiktoken", "safetensors",
        "soundfile", "librosa", "peft", "imageio", "imageio-ffmpeg",
        "python-multipart", "TTS", "einops", "scipy", "torchsde",
        "av", "moviepy", "hf-transfer"
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .run_commands("hf download diffusers/LTX-2.3-Distilled-Diffusers --local-dir /baked_models/ltx_distilled")
    .env({"HF_HOME": "/models/huggingface"})
)

apollo_volume = modal.Volume.from_name("apollo-models-vol", create_if_missing=True)
ltx_volume = modal.Volume.from_name("apollo-models", create_if_missing=True)
hf_secret = modal.Secret.from_name("huggingface-secret")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}

GLOBAL_PIPELINES = {}

# ─── Download de Modelos ──────────────────────────────────────────────────────
@app.function(
    image=apollo_image,
    volumes={"/models": apollo_volume, "/ltx_models": ltx_volume},
    secrets=[hf_secret],
    timeout=7200
)
def download_ai_models():
    from huggingface_hub import snapshot_download
    print("[Apollo] Baixando O ARSENAL COMPLETO para o Pendrive Virtual...")

    modelos = [
        # Imagem
        ("black-forest-labs/FLUX.1-schnell",   "/models/huggingface/hub/models--black-forest-labs--FLUX.1-schnell"),
        ("black-forest-labs/FLUX.1-dev",       "/models/huggingface/hub/models--black-forest-labs--FLUX.1-dev"),
        ("black-forest-labs/FLUX.1-Fill-dev",  "/models/huggingface/hub/models--black-forest-labs--FLUX.1-Fill-dev"),
        # Video
        ("diffusers/LTX-2.3-Distilled-Diffusers",        "/models/huggingface/hub/models--diffusers--LTX-2.3-Distilled-Diffusers"),
        ("Wan-AI/Wan2.1-T2V-14B-Diffusers",    "/models/huggingface/hub/models--Wan-AI--Wan2.1-T2V-14B-Diffusers"),
        # Audio / Voz
        ("openai/whisper-large-v3-turbo",      "/models/huggingface/hub/models--openai--whisper-large-v3-turbo"),
        ("stabilityai/stable-audio-open-1.0",  "/models/huggingface/hub/models--stabilityai--stable-audio-open-1.0"),
        ("coqui/XTTS-v2",                      "/models/huggingface/hub/models--coqui--XTTS-v2"),
    ]
    for repo_id, local_dir in modelos:
        print(f"  ↓ {repo_id}...")
        try:
            snapshot_download(repo_id=repo_id, local_dir=local_dir)
            print(f"  ✅ {repo_id} OK")
        except Exception as e:
            print(f"  ❌ {repo_id} ERRO: {e}")

    try:
        apollo_volume.commit()
    except Exception as e:
        print(f"Warning: Volume commit failed: {e}")
    print("[Apollo] Arsenal baixado com sucesso!")
    return "OK"

# ─── GERAÇÃO DE IMAGEM (Multi-Model) ─────────────────────────────────────────
@app.function(
    image=apollo_image,
    volumes={"/models": apollo_volume},
    secrets=[hf_secret],
    gpu="A100-40GB", # Usando A100 pois o FLUX Dev e Fill exigem
    timeout=600
)
@modal.fastapi_endpoint(method="POST")
def api_generate_image(payload: dict):
    from fastapi.responses import JSONResponse
    import torch

    print(f"[Image Engine] Recebido: {payload}")
    prompt = payload.get("prompt", "a futuristic robot painting a canvas in a neon-lit studio")
    model_id = payload.get("model", "flux_schnell")
    
    # Configuracoes por modelo
    if model_id == "flux_dev":
        model_path = "/models/huggingface/hub/models--black-forest-labs--FLUX.1-dev"
        steps = int(payload.get("steps", 20))
        pipeline_type = "FluxPipeline"
    elif model_id == "flux_fill":
        model_path = "/models/huggingface/hub/models--black-forest-labs--FLUX.1-Fill-dev"
        steps = int(payload.get("steps", 20))
        pipeline_type = "FluxFillPipeline"
    else: # Default: flux_schnell
        model_path = "/models/huggingface/hub/models--black-forest-labs--FLUX.1-schnell"
        steps = int(payload.get("steps", 4))
        pipeline_type = "FluxPipeline"
        
    aspect_ratio = payload.get("aspect_ratio", "horizontal")
    if aspect_ratio == "vertical":
        w, h = 768, 1360
    elif aspect_ratio == "square":
        w, h = 1024, 1024
    else: # horizontal
        w, h = 1360, 768

    try:
        apollo_volume.reload()
        if not os.path.exists(model_path):
            return JSONResponse(status_code=500, content={"error": f"Modelo {model_id} não encontrado no HD."}, headers=CORS_HEADERS)

        print(f"[Image Engine] Carregando {model_id}...")
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

        from diffusers import FluxPipeline, FluxFillPipeline
        
        if pipeline_type == "FluxPipeline":
            pipe = FluxPipeline.from_pretrained(model_path, torch_dtype=torch.bfloat16, local_files_only=True)
            pipe.enable_model_cpu_offload()
            image = pipe(
                prompt,
                guidance_scale=3.5 if model_id != "flux_schnell" else 0.0,
                num_inference_steps=steps,
                max_sequence_length=256,
                height=payload.get("height", h),
                width=payload.get("width", w),
                generator=torch.Generator("cpu").manual_seed(int(time.time()))
            ).images[0]
        else:
            return JSONResponse(status_code=400, content={"error": "Flux Fill endpoint em desenvolvimento (requer upload de imagem base)."}, headers=CORS_HEADERS)

        os.makedirs("/models/outputs", exist_ok=True)
        out_path = f"/models/outputs/img_{int(time.time())}.png"
        image.save(out_path)
        try:
            apollo_volume.commit()
        except Exception as e:
            print(f"Warning: Volume commit failed: {e}")

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return JSONResponse(content={"status": "success", "image_base64": img_b64, "file_saved": out_path, "model": model_id}, headers=CORS_HEADERS)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback.format_exc()}, headers=CORS_HEADERS)

# ─── GERAÇÃO DE VÍDEO (Multi-Model) ──────────────────────────────────────────
@app.function(
    image=apollo_image,
    volumes={"/models": apollo_volume, "/ltx_models": ltx_volume},
    secrets=[hf_secret],
    gpu="A100-80GB", # Upgraded to A100-80GB so 121 frames of LTX at HD won't OOM
    timeout=1200,
    memory=81920,
    scaledown_window=60
)
@modal.fastapi_endpoint(method="POST")
def api_generate_video(payload: dict):
    from fastapi.responses import StreamingResponse
    import torch
    import threading
    import queue
    import json
    import traceback

    print(f"[Video Engine] Recebido: {payload}")
    prompt = payload.get("prompt", "A cinematic drone shot of a futuristic city at night.")
    preset = payload.get("preset", "none")
    
    if preset == "cinematic":
        prompt = f"Cinematic film still, {prompt}, highly detailed, 8k resolution, volumetric lighting, masterpiece, sharp focus, 35mm lens"
    elif preset == "anime":
        prompt = f"Studio Ghibli style, {prompt}, anime key visual, highly detailed, vibrant colors, 2d animation, masterpiece"
    elif preset == "3d":
        prompt = f"3D render, {prompt}, octane render, unreal engine 5, ray tracing, highly detailed, 8k, masterpiece"
    elif preset == "cyberpunk":
        prompt = f"Cyberpunk style, {prompt}, neon lighting, futuristic city, highly detailed, volumetric fog, cinematic masterpiece"
        
    model_id = payload.get("model", "ltx")
    
    q = queue.Queue()
    
    def background_task():
        import torch
        try:
            try:
                apollo_volume.reload()
            except Exception as e:
                print(f"[Warning] Falha ao recarregar volume: {e}")

            if model_id == "wan":
                model_path = "/models/huggingface/hub/models--Wan-AI--Wan2.1-T2V-14B-Diffusers"
                if not os.path.exists(model_path): 
                    q.put({"type": "error", "data": {"error": "Wan2.1 14B não encontrado no HD. Baixe os modelos primeiro."}})
                    return
                if "wan" not in GLOBAL_PIPELINES:
                    from diffusers import WanPipeline, AutoencoderKLWan, WanTransformer3DModel
                    from diffusers.utils import export_to_video
                    from diffusers.schedulers.scheduling_unipc_multistep import UniPCMultistepScheduler
                    import subprocess
                    import base64
                    
                    vae = AutoencoderKLWan.from_pretrained(
                        model_path,
                        subfolder="vae",
                        torch_dtype=torch.float32,
                        local_files_only=True
                    )
                    
                    transformer = WanTransformer3DModel.from_pretrained(
                        model_path,
                        subfolder="transformer",
                        torch_dtype=torch.bfloat16,
                        local_files_only=True
                    )
                    transformer.enable_layerwise_casting(
                        storage_dtype=torch.float8_e5m2,
                        compute_dtype=torch.bfloat16,
                    )
                    
                    pipe = WanPipeline.from_pretrained(
                        model_path,
                        vae=vae,
                        transformer=transformer,
                        torch_dtype=torch.bfloat16,
                        local_files_only=True
                    )
                    
                    pipe.scheduler = UniPCMultistepScheduler.from_config(
                        pipe.scheduler.config,
                        flow_shift=3.0,
                    )
                    
                    pipe.enable_model_cpu_offload()
                    pipe.vae.enable_tiling()
                    pipe.vae.enable_slicing()
                    GLOBAL_PIPELINES["wan"] = pipe
                    warm_start = False
                else:
                    pipe = GLOBAL_PIPELINES["wan"]
                    from diffusers.utils import export_to_video
                    import subprocess
                    import base64
                    warm_start = True
                
                duration = int(payload.get("duration", 5))
                num_frames = (duration * 16) + 1
                aspect_ratio = payload.get("aspect_ratio", "horizontal")
                quality = payload.get("quality", "hd")
                
                w, h = 832, 480
                if aspect_ratio == "vertical": w, h = 480, 832
                elif aspect_ratio == "square": w, h = 480, 480
                if quality == "fhd": w, h = 1280, 720
                if "width" in payload: w = int(payload["width"])
                if "height" in payload: h = int(payload["height"])
                if "num_frames" in payload: num_frames = int(payload["num_frames"])
                
                total_steps = int(payload.get("steps", 40))
                def wan_progress_callback(pipe_ref, step_index, timestep, callback_kwargs):
                    p = int(((step_index + 1) / total_steps) * 100)
                    if p % 5 == 0 or p == 100:
                        q.put({"type": "progress", "data": {"status": "progress", "progress": p}})
                    return callback_kwargs
                
                seed = int(payload.get("seed", -1))
                generator = torch.Generator("cuda").manual_seed(seed) if seed != -1 else None

                init_image = None
                if "image_base64" in payload:
                    import io
                    from PIL import Image
                    image_data = base64.b64decode(payload["image_base64"])
                    init_image = Image.open(io.BytesIO(image_data)).convert("RGB")
                    # Warning: Proper Wan I2V might require WanImageToVideoPipeline
                    # This passes it as kwargs for compatibility.

                kwargs = {
                    "prompt": prompt,
                    "negative_prompt": payload.get("negative_prompt", "worst quality, inconsistent, blurry, deformed"),
                    "num_inference_steps": total_steps,
                    "guidance_scale": float(payload.get("guidance_scale", 3.0)),
                    "width": w,
                    "height": h,
                    "num_frames": num_frames,
                    "callback_on_step_end": wan_progress_callback,
                    "generator": generator,
                }
                if init_image is not None:
                    kwargs["image"] = init_image

                output = pipe(**kwargs)
                
                video_frames = output.frames[0]
                video_path = "/tmp/output_wan.mp4"
                export_to_video(video_frames, video_path, fps=16)
                
                with open(video_path, "rb") as f:
                    video_b64 = base64.b64encode(f.read()).decode("utf-8")
                    
                q.put({"type": "success", "data": {"status": "success", "video_base64": video_b64, "model": model_id, "warm_start": warm_start}})
            else: # LTX
                model_id_hf = "diffusers/LTX-2.3-Distilled-Diffusers"
                cache_dir = "/baked_models/ltx_distilled"
                if not os.path.exists(cache_dir): 
                    q.put({"type": "error", "data": {"error": "LTX 2.3 Distilled não encontrado na imagem Docker embutida. Faça o redeploy com o cache."}})
                    return
                
                if "ltx" not in GLOBAL_PIPELINES:
                    from diffusers import LTX2Pipeline
                    from diffusers.utils import export_to_video
                    import subprocess
                    import scipy.io.wavfile
                    import base64
                    import torch
                    
                    pipe = LTX2Pipeline.from_pretrained(
                        cache_dir,
                        torch_dtype=torch.bfloat16,
                        local_files_only=True
                    )
                    pipe.enable_model_cpu_offload()
                    pipe.vae.enable_tiling()
                    pipe.vae.enable_slicing()
                    GLOBAL_PIPELINES["ltx"] = pipe
                    warm_start = False
                else:
                    pipe = GLOBAL_PIPELINES["ltx"]
                    from diffusers.utils import export_to_video
                    import subprocess
                    import scipy.io.wavfile
                    import base64
                    import torch
                    warm_start = True
                
                duration = int(payload.get("duration", 5))
                num_frames = (duration * 24) + 1
                aspect_ratio = payload.get("aspect_ratio", "horizontal")
                quality = payload.get("quality", "hd")
                
                w, h = 768, 512
                if aspect_ratio == "vertical": w, h = 512, 768
                elif aspect_ratio == "square": w, h = 768, 768
                
                if quality == "fhd":
                    if aspect_ratio == "vertical":
                        w = 576
                        h = 1024
                    elif aspect_ratio == "square":
                        w = 1024
                        h = 1024
                    else:
                        w = 1024
                        h = 576
                elif quality == "fast":
                    if aspect_ratio == "vertical":
                        w = 416
                        h = 704
                    elif aspect_ratio == "square":
                        w = 512
                        h = 512
                    else:
                        w = 704
                        h = 416
                    
                if "width" in payload: w = int(payload["width"])
                if "height" in payload: h = int(payload["height"])
                if "num_frames" in payload: num_frames = int(payload["num_frames"])
                
                total_steps = int(payload.get("steps", 8))
                def ltx_progress_callback(pipe_ref, step_index, timestep, callback_kwargs):
                    p = int(((step_index + 1) / total_steps) * 100)
                    if p % 5 == 0 or p == 100:
                        q.put({"type": "progress", "data": {"status": "progress", "progress": p}})
                    return callback_kwargs

                seed = int(payload.get("seed", -1))
                generator = torch.Generator("cuda").manual_seed(seed) if seed != -1 else None

                init_image = None
                if payload.get("image_base64"):
                    import io
                    from PIL import Image
                    image_data = base64.b64decode(payload["image_base64"])
                    init_image = Image.open(io.BytesIO(image_data)).convert("RGB")

                kwargs = {
                    "prompt": prompt,
                    "negative_prompt": payload.get("negative_prompt", "low quality, worst quality, blurry, deformed, distorted, washed out, jitter, flicker, jpeg artifacts, glitch, bad anatomy, extra limbs, text, subtitles, watermark"),
                    "num_inference_steps": total_steps,
                    "guidance_scale": 1.0,
                    "width": w,
                    "height": h,
                    "num_frames": num_frames,
                    "callback_on_step_end": ltx_progress_callback,
                    "generator": generator,
                }
                if init_image is not None:
                    kwargs["image"] = init_image
                    from diffusers import LTX2ImageToVideoPipeline
                    components = dict(pipe.components)
                    pipe_i2v = LTX2ImageToVideoPipeline(**components)

                    output = pipe_i2v(**kwargs)
                else:
                    output = pipe(**kwargs)
                
                from diffusers.pipelines.ltx2.export_utils import encode_video
                
                video = getattr(output, "frames", None)
                if video is None and isinstance(output, dict):
                    video = output.get("frames", output.get("videos"))
                    
                audio = getattr(output, "audio", getattr(output, "audios", None))
                if audio is None and isinstance(output, dict):
                    audio = output.get("audio", output.get("audios"))
                
                # Check for list of lists
                if isinstance(video, list) and len(video) > 0 and isinstance(video[0], list):
                    video = video[0]
                
                video_path = "/tmp/output_ltx.mp4"
                
                audio_sample_rate = 48000
                if hasattr(pipe, "vocoder") and hasattr(pipe.vocoder, "config"):
                    audio_sample_rate = pipe.vocoder.config.output_sampling_rate
                
                os.makedirs("/models/outputs", exist_ok=True)
                t_stamp = int(time.time())
                out_path = f"/tmp/vid_{t_stamp}.mp4"
                
                if audio is not None and len(audio) > 0 and audio[0] is not None:
                    encode_video(
                        video,
                        fps=24,
                        audio=audio[0].float().cpu() if hasattr(audio[0], "float") else audio[0],
                        audio_sample_rate=audio_sample_rate,
                        output_path=out_path,
                    )
                else:
                    from diffusers.utils import export_to_video
                    export_to_video(video, out_path, fps=24)
                        
                # (removed volume commit)

                with open(out_path, "rb") as vf:
                    video_b64 = base64.b64encode(vf.read()).decode("utf-8")
                q.put({"type": "success", "data": {"status": "success", "video_base64": video_b64, "file_saved": out_path, "model": model_id, "warm_start": warm_start}})

        except Exception as e:
            q.put({"type": "error", "data": {"error": str(e), "traceback": traceback.format_exc()}})

    t = threading.Thread(target=background_task)
    t.start()
    
    def stream_generator():
        while True:
            try:
                # A cada 10 segundos, checa a fila. Se não houver nada, envia um espaço (keep-alive)
                msg = q.get(timeout=10)
                yield json.dumps(msg["data"]) + "\n"
                if msg["type"] in ["success", "error"]:
                    break
            except queue.Empty:
                yield " "
                
    return StreamingResponse(stream_generator(), media_type="application/json", headers=CORS_HEADERS)

# ─── GERAÇÃO DE ÁUDIO / VOZ (Multi-Model) ────────────────────────────────────
@app.function(
    image=apollo_image,
    volumes={"/models": apollo_volume},
    secrets=[hf_secret],
    gpu="A10G", 
    timeout=600
)
@modal.fastapi_endpoint(method="POST")
def api_generate_audio(payload: dict):
    from fastapi.responses import JSONResponse
    import torch

    model_id = payload.get("model", "xtts")
    text = payload.get("text", "Olá, este é um teste de áudio no Apollo Modal.")

    try:
        apollo_volume.reload()
        os.makedirs("/models/outputs", exist_ok=True)
        out_path = f"/models/outputs/aud_{int(time.time())}.wav"

        if model_id == "xtts":
            from TTS.api import TTS
            model_path = "/models/huggingface/hub/models--coqui--XTTS-v2"
            
            # Necessario definir variaveis de ambiente pro XTTS aceitar os termos offline
            os.environ["COQUI_TOS_AGREED"] = "1"
            
            # Inicializar TTS (como estamos offline, apontamos o config path se necessario, ou confiamos no cache)
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda" if torch.cuda.is_available() else "cpu")
            
            # XTTS requer uma voz de referencia. Se não houver, falhamos amigavelmente ou usamos uma padrao.
            # No momento, retornamos placeholder.
            return JSONResponse(status_code=400, content={"error": "XTTS requer arquivo de speaker reference. Em implementacao."}, headers=CORS_HEADERS)

        elif model_id == "stable_audio":
            model_path = "/models/huggingface/hub/models--stabilityai--stable-audio-open-1.0"
            from diffusers import StableAudioPipeline
            import scipy.io.wavfile

            pipe = StableAudioPipeline.from_pretrained(model_path, torch_dtype=torch.float16, local_files_only=True)
            pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

            generator = torch.Generator("cuda").manual_seed(int(time.time()))
            audio = pipe(
                prompt=text,
                guidance_scale=7.0,
                num_inference_steps=200,
                audio_end_in_s=10.0,
                num_waveforms_per_prompt=1,
                generator=generator,
            ).audios

            output = audio[0].T.float().cpu().numpy()
            scipy.io.wavfile.write(out_path, pipe.vae.sampling_rate, output)
            try:
                apollo_volume.commit()
            except Exception as e:
                print(f"Warning: Volume commit failed: {e}")

            with open(out_path, "rb") as af:
                aud_b64 = base64.b64encode(af.read()).decode("utf-8")
            return JSONResponse(content={"status": "success", "audio_base64": aud_b64, "file_saved": out_path, "model": model_id}, headers=CORS_HEADERS)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback.format_exc()}, headers=CORS_HEADERS)

# ─── TRANSCRIÇÃO DE ÁUDIO (Whisper) ────────────────────────────────────────────
@app.function(
    image=apollo_image,
    volumes={"/models": apollo_volume},
    secrets=[hf_secret],
    gpu="A10G", 
    timeout=600
)
@modal.fastapi_endpoint(method="POST")
def api_transcribe(payload: dict):
    from fastapi.responses import JSONResponse
    import torch
    import io
    import base64
    import time
    import traceback

    try:
        if "audio_base64" not in payload:
            return JSONResponse(status_code=400, content={"error": "Falta audio_base64"}, headers=CORS_HEADERS)

        apollo_volume.reload()
        os.makedirs("/models/outputs", exist_ok=True)
        out_path = f"/models/outputs/transcribe_{int(time.time())}.wav"

        audio_data = base64.b64decode(payload["audio_base64"])
        with open(out_path, "wb") as f:
            f.write(audio_data)

        from transformers import pipeline
        # Usar o diretorio oficial do cache do HuggingFace baixado pelo script
        model_id = "openai/whisper-large-v3-turbo"
        
        # O huggingface usa os symlinks em /root/.cache, mas pra garantir o offline:
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            chunk_length_s=30,
            device="cuda" if torch.cuda.is_available() else "cpu",
            model_kwargs={"local_files_only": True}
        )

        result = pipe(out_path, generate_kwargs={"task": "transcribe"})
        text = result["text"]

        return JSONResponse(content={"status": "success", "text": text}, headers=CORS_HEADERS)

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback.format_exc()}, headers=CORS_HEADERS)


# ─── PING / DEBUG ──────────────────────────────────────────────────────────────
@app.function(image=apollo_image, volumes={"/models": apollo_volume})
@modal.fastapi_endpoint(method="GET")
def api_ping():
    from fastapi.responses import JSONResponse
    return JSONResponse(content={"status": "online", "message": "Apollo Super Engine ativa!"}, headers=CORS_HEADERS)
