"""
Apollo Modal Router
===================
Este â”œÂ® o Roteador Central (Gateway).
Ele recebe requisiâ”œÂºâ”œÃes JSON da sua API/Backend Node/PHP/etc.,
identifica qual modelo (LTX 13B ou Wan) o usuâ”œÃ­rio escolheu
baseado no preset, e dispara o comando de forma assâ”œÂ¡ncrona (ou aguarda)
direto para as GPUs especâ”œÂ¡ficas (L4 ou A100).
# Modificado para forcar deploy
"""

import modal # force rebuild 5
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append("/root")
sys.path.append("/pkg")
sys.path.append("/")

# Imports top-level para garantir que o Modal faâ”œÂºa o trace e os publique junto com o app
import backend.cloud_tools.engines.wan_engine
import backend.cloud_tools.engines.ltx_engine
import backend.cloud_tools.engines.flux_engine
import backend.cloud_tools.engines.flux_txt2img_engine
import backend.cloud_tools.engines.moss_engine
import backend.cloud_tools.engines.universal_engine
import backend.cloud_tools.engines.lora_training_engine
from backend.cloud_tools.engines.flux_engine import Flux2ComfyEngine_V2

# Voz
import backend.cloud_tools.engines.stt_engine
import backend.cloud_tools.engines.tts_engine
import backend.cloud_tools.engines.qwen_tts_clone_engine
import backend.cloud_tools.engines.ace_step_comfy_engine

from backend.cloud_tools.modal_app import app

# FORCE_REBUILD = 5

router_image = (
    modal.Image.debian_slim()
    .pip_install("fastapi[standard]", "pydantic", "requests")
    .add_local_python_source("backend")
    .add_local_dir("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API", remote_path="/workflows")
)

web_app = FastAPI(title="Apollo Render API")

# Configuraâ”œÂºâ”œÃºo de CORS para permitir requisiâ”œÂºâ”œÃes do Frontend React (localhost ou Vercel/Netlify)
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AudioLabRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = None
    model: str = "sa3" # "sa3", "minimax", "ace-step"
    duration: int = 30
    
class VideoRequest(BaseModel):
    prompt: str
    image_base64: Optional[str] = None  # Imagem opcional para o Image-to-Video
    model: str = "wan"  # "wan" (L4/A100) ou "ltx" (A100)
    preset: str = "fast" # "fast", "standard", "pro"
    aspect_ratio: str = "horizontal" # "horizontal", "vertical", "square"
    duration: int = 5
    seed: int = 42

class ImageRequest(BaseModel):
    prompt: str
    model: str = "flux-schnell" # "flux-schnell", "flux-dev"
    format: str = "horizontal" # "horizontal", "vertical", "square"
    aspect_ratio: str = "horizontal" # alias aceito pelo frontend
    seed: int = 42
    reference_images_base64: Optional[list[str]] = None
    use_upscale: bool = True  # Se False, retorna a imagem base sem upscale
    lora_name: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    reference_audio_base64: Optional[str] = None
    instruct: Optional[str] = None
    engine: str = "xtts" # "xtts", "moss" ou "qwen"
    ref_text: Optional[str] = None

class UniversalRequest(BaseModel):
    workflow: dict
    input_node_id: str
    input_value: str
    output_node_id: str

class MultiPassRequest(BaseModel):
    workflow: dict
    base_prompt: str
    regional_prompts: list[str]
    input_images_b64: list[str]
    seed: int = 42
    use_upscale: bool = False  # Se False, retorna a imagem base sem upscale
    lora_name: Optional[str] = None

class TrainLoraRequest(BaseModel):
    user_id: str
    character_name: str
    images_b64: list[str]
    trigger_word: str = "ohwx"

@web_app.post("/generate/image")
def api_generate_image(req: ImageRequest):
    import json
    try:
        model = req.model.lower()
        if model != "flux2-universal":
            return {"status": "error", "message": f"ERRO: Somente FLUX 2 DEV suportado (flux2-universal)."}
            
        if req.reference_images_base64:
            from backend.cloud_tools.engines.flux_engine import Flux2ComfyEngine_V2
            engine = Flux2ComfyEngine_V2()
            print(f"[Router] Spawning Flux2ComfyEngine_V2 (Img2Img - PuLID) -> format: {req.format}")
        else:
            # Dummy comment to force deploy V5
            from backend.cloud_tools.engines.flux_txt2img_engine import Flux2Txt2ImgEngine
            engine = Flux2Txt2ImgEngine()
            print(f"[Router] Spawning Flux2Txt2ImgEngine (Txt2Img) -> format: {req.format}")
        
        # Resolve formato: usa req.format, com fallback para req.aspect_ratio
        resolved_format = req.format if req.format != "horizontal" else req.aspect_ratio
        job = engine.generate.spawn(
            prompt=req.prompt,
            aspect_ratio=resolved_format,
            seed=req.seed,
            reference_images_base64=req.reference_images_base64,
            input_image_b64=req.reference_images_base64[0] if req.reference_images_base64 else None,
            use_upscale=req.use_upscale
        )
        
        async def stream_result_comfyui():
            from modal.functions import FunctionCall
            fc = FunctionCall.from_id(job.object_id)
            final_res = None
            while True:
                try:
                    final_res = await fc.get.aio(timeout=5.0)
                    break
                except TimeoutError:
                    yield " \n"
                except Exception as e:
                    yield json.dumps({"status": "error", "message": f"Erro na Modal: {str(e)}"}) + "\n"
                    return
            
            if final_res and final_res.get("status") == "success":
                yield json.dumps(final_res) + "\n"
            else:
                yield json.dumps(final_res) + "\n"
                
        return StreamingResponse(stream_result_comfyui(), media_type="application/x-ndjson")
    
    except Exception as e:
        return {"status": "error", "message": f"Erro interno de Roteamento de Imagem: {str(e)}"}

@web_app.post("/generate/video")
def api_generate_video(req: VideoRequest):
    # Roteamento baseado no modelo
    try:
        model = req.model.lower()
        preset = req.preset.lower()
        
        # Limite agressivo sugerido para I2V no LTX (Prevenâ”œÂºâ”œÃºo de VRAM OOM)
        if model == "ltx" and preset == "fast" and req.image_base64:
            if req.duration > 2:
                return {
                    "status": "error", 
                    "error_type": "invalid_duration",
                    "message": f"Modo FAST I2V suporta no mâ”œÃ­ximo 2s. Use modo PRO para duraâ”œÂºâ”œÃes maiores."
                }
        
        if model == "ltx":
            # Dispara na GPU A100 (Tier 2)
            from backend.cloud_tools.engines.ltx_engine import LTX13BEngine
            engine = LTX13BEngine()
            print(f"[Router] Spawning LTX13BEngine (A100) -> preset: {req.preset}")
            
        elif model == "wan":
            # Dispara na GPU
            from backend.cloud_tools.engines.wan_engine import Wan21Engine
            engine = Wan21Engine()
            print(f"[Router] Spawning Wan21Engine -> preset: {req.preset}")
            
        else:
            return {"status": "error", "message": f"Modelo desconhecido: {model}. Use 'ltx' ou 'wan'."}
            
        # Spawn assâ”œÂ¡ncrono para evitar o limite de 150s do Modal HTTP Gateway
        job = engine.generate.spawn(
            prompt=req.prompt,
            image_base64=req.image_base64,
            duration=req.duration,
            preset=req.preset,
            aspect_ratio=req.aspect_ratio,
            seed=req.seed
        )
        
        async def stream_result():
            from modal.functions import FunctionCall
            fc = FunctionCall.from_id(job.object_id)
            while True:
                try:
                    # Tenta pegar o resultado com timeout curto. 
                    # Se nâ”œÃºo terminou, cai no TimeoutError e envia um espaâ”œÂºo (heartbeat)
                    res = await fc.get.aio(timeout=5.0)
                    yield json.dumps(res)
                    break
                except TimeoutError:
                    yield " "
                except Exception as e:
                    yield json.dumps({"status": "error", "message": f"Erro interno da Modal: {str(e)}"})
                    break
                    
        return StreamingResponse(stream_result(), media_type="application/json")

    except Exception as e:
        return {"status": "error", "message": f"Erro interno de Roteamento: {str(e)}"}

@web_app.post("/generate/tts")
def api_generate_tts(req: TTSRequest):
    try:
        engine_choice = req.engine.lower()
        if engine_choice == "qwen":
            from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine
            engine = QwenTtsCloneEngine()
            print(f"[Router] Spawning QwenTtsCloneEngine -> Text: {req.text[:30]}...")
            
            ref_text = req.ref_text
            if not ref_text and req.reference_audio_base64:
                from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT
                stt = WhisperTurboSTT()
                print("[Router] Transcrevendo ref_audio para ICL do Qwen...")
                import base64
                ref_bytes = base64.b64decode(req.reference_audio_base64)
                stt_res = stt.transcribe.remote(ref_bytes)
                if isinstance(stt_res, dict) and stt_res.get("status") == "success":
                    ref_text = stt_res.get("text", "")
                else:
                    return {"status": "error", "message": "Falha no WhisperTurboSTT"}

            fc = engine.clone.spawn(
                text=req.text,
                ref_audio_b64=req.reference_audio_base64,
                ref_text=ref_text or "",
                language="Portuguese",
                instruct=req.instruct or ""
            )
        else:
            from backend.cloud_tools.engines.moss_engine import MossTTSEngine
            engine = MossTTSEngine()
            
            print(f"[Router] Spawning MossTTSEngine (H100) -> Text: {req.text[:30]}...")
            
            ref_bytes = None
            if req.reference_audio_base64:
                import base64
                ref_bytes = base64.b64decode(req.reference_audio_base64)
                
            fc = engine.generate_voice.spawn(req.text, ref_bytes)
        
        # Como o TTS pode demorar dezenas de segundos, precisamos de Streaming de ping
        async def stream_result():
            import json
            while True:
                try:
                    res = await fc.get.aio(timeout=5.0)
                    if isinstance(res, dict):
                        # Qwen return
                        yield json.dumps(res)
                    else:
                        # Moss return (bytes)
                        import base64
                        b64_audio = base64.b64encode(res).decode('utf-8')
                        yield json.dumps({"status": "success", "audio_base64": b64_audio})
                    break
                except TimeoutError:
                    yield " "
                except Exception as e:
                    yield json.dumps({"status": "error", "message": f"Erro interno TTS: {str(e)}"})
                    break
                    
        return StreamingResponse(stream_result(), media_type="application/json")
    
    except Exception as e:
        return {"status": "error", "message": f"Erro de roteamento TTS: {str(e)}"}

@web_app.post("/generate/universal")
def api_generate_universal(req: UniversalRequest):
    try:
        from backend.cloud_tools.engines.universal_comfy_engine import UniversalComfyEngine
        engine = UniversalComfyEngine()
        
        job = engine.generate.spawn(
            workflow=req.workflow,
            input_node_id=req.input_node_id,
            input_value=req.input_value,
            output_node_id=req.output_node_id
        )
        
        async def stream_result():
            from modal.functions import FunctionCall
            fc = FunctionCall.from_id(job.object_id)
            try:
                # Iterate over the generator asynchronously
                async for chunk in fc:
                    yield json.dumps(chunk) + "\n"
            except Exception as e:
                yield json.dumps({"type": "error", "message": f"Erro interno da Modal (Generator): {str(e)}"}) + "\n"
                    
        return StreamingResponse(stream_result(), media_type="application/x-ndjson")
    except Exception as e:
        return {"status": "error", "message": f"Erro de roteamento Universal: {str(e)}"}

@web_app.post("/generate/multipass")
def api_generate_multipass(req: MultiPassRequest):
    try:
        import json
        from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine
        engine = UniversalComfyEngine()
        
        print(f"[Router] Spawning UniversalComfyEngine Multipass -> Prompt: {req.base_prompt[:30]}...")
        
        if req.use_upscale:
            if "9" in req.workflow:
                del req.workflow["9"]
            
            with open("/workflows/image_flux2_text_to_image_upscale.json", "r", encoding="utf-8") as f:
                upscale_full = json.load(f)
            
            vae_decode_id = None
            for node_id, node_data in req.workflow.items():
                if isinstance(node_data, dict) and node_data.get("class_type") == "VAEDecode":
                    vae_decode_id = str(node_id)
                    break
            
            if vae_decode_id and "upscale_12" in upscale_full:
                upscale_full["upscale_12"]["inputs"]["image"] = [vae_decode_id, 0]
            
            for k, v in upscale_full.items():
                if k.startswith("upscale_"):
                    req.workflow[k] = v
        
        job = engine.generate.spawn(
            workflow_json_string=json.dumps(req.workflow),
            prompt=req.base_prompt,
            input_images_b64=req.input_images_b64,
            regional_prompts=req.regional_prompts,
            seed=req.seed
        )
        
        async def stream_result():
            try:
                from modal.functions import FunctionCall
                import asyncio
                fc = FunctionCall.from_id(job.object_id)
                
                task = asyncio.create_task(fc.get.aio(timeout=1200))
                
                while not task.done():
                    yield json.dumps({"status": "processing", "message": "Heartbeat"}) + "\n"
                    done, pending = await asyncio.wait([task], timeout=10.0)
                    if done:
                        break
                        
                res = task.result()
                
                if res and res.get("status") == "success":
                    yield json.dumps(res) + "\n"
                else:
                    yield json.dumps(res) + "\n"
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                yield json.dumps({"status": "error", "message": f"Erro interno Multipass: {str(e)}", "trace": error_trace}) + "\n"
                    
        return StreamingResponse(stream_result(), media_type="application/x-ndjson")
    except Exception as e:
        return {"status": "error", "message": f"Erro de roteamento Multipass: {str(e)}"}

@web_app.post("/generate/autoblog/multipass")
def api_generate_autoblog_multipass(req: MultiPassRequest):
    try:
        import json
        from backend.cloud_tools.engines.universal_engine import BlogUniversalComfyEngine
        engine = BlogUniversalComfyEngine()
        
        print(f"[Router] Spawning BlogUniversalComfyEngine Multipass -> Prompt: {req.base_prompt[:30]}...")
        
        if req.use_upscale:
            if "9" in req.workflow:
                del req.workflow["9"]
            
            with open("/workflows/image_flux2_text_to_image_upscale.json", "r", encoding="utf-8") as f:
                upscale_full = json.load(f)
            
            vae_decode_id = None
            for node_id, node_data in req.workflow.items():
                if isinstance(node_data, dict) and node_data.get("class_type") == "VAEDecode":
                    vae_decode_id = str(node_id)
                    break
            
            if vae_decode_id and "upscale_12" in upscale_full:
                upscale_full["upscale_12"]["inputs"]["image"] = [vae_decode_id, 0]
            
            for k, v in upscale_full.items():
                if k.startswith("upscale_"):
                    req.workflow[k] = v
        
        job = engine.generate.spawn(
            workflow_json_string=json.dumps(req.workflow),
            prompt=req.base_prompt,
            input_images_b64=req.input_images_b64,
            regional_prompts=req.regional_prompts,
            seed=req.seed,
            lora_name=req.lora_name
        )
        
        async def stream_result():
            try:
                from modal.functions import FunctionCall
                import asyncio
                fc = FunctionCall.from_id(job.object_id)
                
                task = asyncio.create_task(fc.get.aio(timeout=1200))
                
                while not task.done():
                    yield json.dumps({"status": "processing", "message": "Heartbeat"}) + "\n"
                    done, pending = await asyncio.wait([task], timeout=10.0)
                    if done:
                        break
                        
                res = task.result()
                
                if res and res.get("status") == "success":
                    yield json.dumps(res) + "\n"
                else:
                    yield json.dumps(res) + "\n"
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                yield json.dumps({"status": "error", "message": f"Erro interno Multipass: {str(e)}", "trace": error_trace}) + "\n"
                    
        return StreamingResponse(stream_result(), media_type="application/x-ndjson")
    except Exception as e:
        return {"status": "error", "message": f"Erro de roteamento Multipass: {str(e)}"}

@web_app.post("/train_lora")
def api_train_lora(req: TrainLoraRequest):
    try:
        from backend.cloud_tools.engines.lora_training_engine import FluxLoraTrainer
        engine = FluxLoraTrainer()
        
        job = engine.train_lora.spawn(
            user_id=req.user_id,
            character_name=req.character_name,
            images_b64=req.images_b64,
            trigger_word=req.trigger_word
        )
        
        return {"status": "processing", "job_id": job.object_id, "message": "Treinamento iniciado no Modal (A100/H100)"}
    except Exception as e:
        return {"status": "error", "message": f"Erro de roteamento LoRA: {str(e)}"}

@web_app.get("/list_loras/{user_id}")
def api_list_loras(user_id: str):
    import os
    try:
        user_dir = f"/comfyui_models/loras/users/{user_id}"
        if not os.path.exists(user_dir):
            return {"status": "success", "loras": []}
            
        loras = [f for f in os.listdir(user_dir) if f.endswith(".safetensors")]
        # Retornar o caminho relativo ao diretorio de loras do ComfyUI
        # O ComfyUI procura em /comfyui/models/loras/
        # Nosso script faz symlink de /comfyui_models/loras -> /comfyui/models/loras
        # Entao o lora_name no JSON deve ser "users/master_user_1/nome.safetensors"
        
        lora_paths = [f"users/{user_id}/{lora}" for lora in loras]
        return {"status": "success", "loras": lora_paths}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@web_app.get("/ping")
def api_ping():
    return {
        "status": "online",
        "router": "Apollo Multi-Tier Router",
        "engines_disponiveis": {
            "wan": "Wan2.1 (NVIDIA L4/A100) - Presets: fast, standard, pro",
            "ltx": "LTX-Video-13B (NVIDIA A100) - Presets: fast, pro",
            "flux-schnell": "FLUX.1-schnell (NVIDIA L4)",
            "flux-dev": "FLUX.1-dev (NVIDIA A10G) - Alta Qualidade",
            "flux-pulid": "FLUX.1-dev + PuLID (NVIDIA A10G) - Consistencia Facial",
            "moss-tts": "MOSS-TTS 8B (NVIDIA H100) - Voice Cloning"
        }
    }

from backend.cloud_tools.engines.universal_engine import apollo_volume
@web_app.post("/generate/audio_lab")
def api_generate_audio_lab(req: AudioLabRequest):
    try:
        model = req.model.lower()
        if model == "sa3":
            from backend.cloud_tools.engines.stable_audio_engine import StableAudioEngine
            engine = StableAudioEngine()
            print(f"[Router] Spawning StableAudioEngine for SA3")
            fc = engine.generate_audio.spawn(prompt=req.prompt, duration_s=float(req.duration))
            res = fc.get()
            if isinstance(res, bytes):
                import base64
                b64 = base64.b64encode(res).decode('utf-8')
                return {"status": "success", "audio_base64": b64, "message": "SA3 Recebido da Nuvem!"}
            return {"status": "error", "error_type": "generation_failed", "message": "Erro na geracao SA3"}
            
        elif model == "minimax":
            from backend.cloud_tools.engines.minimax_engine import MinimaxEngine
            engine = MinimaxEngine()
            print(f"[Router] Spawning MinimaxEngine")
            is_instrumental = not bool(req.lyrics)
            fc = engine.generate.spawn(prompt=req.prompt, is_instrumental=is_instrumental, lyrics=req.lyrics or "", duration=float(req.duration))
            res = fc.get()
            if isinstance(res, bytes):
                import base64
                b64 = base64.b64encode(res).decode('utf-8')
                return {"status": "success", "audio_base64": b64, "message": "MiniMax Recebido da Nuvem!"}
            return {"status": "error", "error_type": "generation_failed", "message": "Erro na geracao MiniMax"}
            
        elif model == "ace-step":
            from backend.cloud_tools.engines.ace_step_python_engine import AceStepPythonEngine
            engine = AceStepPythonEngine()
            print(f"[Router] Spawning AceStepPythonEngine")
            fc = engine.generate.spawn(style_tags=req.prompt, lyrics=req.lyrics or "", length_seconds=req.duration)
            res = fc.get()
            if isinstance(res, dict) and "audio_base64" in res:
                return {"status": "success", "audio_base64": res["audio_base64"], "message": "ACE-Step Recebido da Nuvem!"}
            return {"status": "error", "error_type": "generation_failed", "message": "Erro na geracao ACE-Step"}
            
        else:
            return {"status": "error", "error_type": "invalid_model", "message": f"Modelo {model} nao suportado."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error_type": "exception", "message": str(e), "traceback": traceback.format_exc()}

@app.function(
    image=router_image,
    volumes={"/apollo_volume": apollo_volume}
)
def clean_antelope():
    import os, shutil
    path = "/apollo_volume/models/insightface/models/antelopev2"
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
    print("Cleaned antelopev2!")

@app.function(
    image=router_image,
    timeout=1200
)
@modal.asgi_app()
def apollo_api():
    return web_app

