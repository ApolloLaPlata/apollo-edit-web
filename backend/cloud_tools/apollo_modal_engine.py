"""
Apollo Modal Router
===================
Este é o Roteador Central (Gateway).
Ele recebe requisições JSON da sua API/Backend Node/PHP/etc.,
identifica qual modelo (LTX 13B ou Wan) o usuário escolheu
baseado no preset, e dispara o comando de forma assíncrona (ou aguarda)
direto para as GPUs específicas (L4 ou A100).
# Modificado para forcar deploy
"""

import modal
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

# Imports top-level para garantir que o Modal faça o trace e os publique junto com o app
import backend.cloud_tools.engines.wan_engine
import backend.cloud_tools.engines.ltx_engine
import backend.cloud_tools.engines.flux_engine
import backend.cloud_tools.engines.flux_txt2img_engine
import backend.cloud_tools.engines.moss_engine
import backend.cloud_tools.engines.universal_engine
from backend.cloud_tools.engines.flux_engine import Flux2ComfyEngine_V2

from backend.cloud_tools.modal_app import app

# FORCE_REBUILD = 5

router_image = (
    modal.Image.debian_slim()
    .pip_install("fastapi[standard]", "pydantic", "requests")
    .add_local_python_source("backend")
    .add_local_dir("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API", remote_path="/workflows")
)

web_app = FastAPI(title="Apollo Render API")

# Configuração de CORS para permitir requisições do Frontend React (localhost ou Vercel/Netlify)
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class TTSRequest(BaseModel):
    text: str
    reference_audio_base64: Optional[str] = None

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
    use_upscale: bool = True  # Se False, retorna a imagem base sem upscale

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
            input_image_b64=req.reference_images_base64[0] if req.reference_images_base64 else None
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
                    yield json.dumps({"status": "error", "message": f"Erro na Modal (Base): {str(e)}"}) + "\n"
                    return
            
            if final_res and final_res.get("status") == "success":
                if not req.use_upscale:
                    # Sem upscale: retorna a imagem base diretamente
                    print("[Router] use_upscale=False — retornando imagem base sem upscale.")
                    yield json.dumps(final_res) + "\n"
                else:
                    # FASE 2: UPSCALE (quando use_upscale=True)
                    try:
                        yield " \n"
                        from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine
                        upscale_engine = UniversalComfyEngine()
                        
                        import os
                        workflow_path = os.path.join(os.path.dirname(__file__), "..", "..", "Comfyui Workflow API", "flux_upscale_ultrasharp.json")
                        with open(workflow_path, "r", encoding="utf-8") as f:
                            upscale_json = f.read()
                        
                        upscale_job = upscale_engine.generate.spawn(
                            workflow_json_string=upscale_json,
                            prompt=req.prompt,
                            input_image_b64=final_res["image_base64"],
                            is_upscale=True,
                            denoise=0.25
                        )
                        upscale_fc = FunctionCall.from_id(upscale_job.object_id)
                        while True:
                            try:
                                up_res = await upscale_fc.get.aio(timeout=5.0)
                                yield json.dumps(up_res) + "\n"
                                break
                            except TimeoutError:
                                yield " \n"
                            except Exception as e:
                                yield json.dumps({"status": "error", "message": f"Erro na Modal (Upscale): {str(e)}"}) + "\n"
                                break
                    except Exception as e:
                        yield json.dumps({"status": "error", "message": f"Erro no Roteamento Upscale: {str(e)}"}) + "\n"
            else:
                # Falhou na geração base, apenas retorna o erro
                if final_res:
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
        
        # Limite agressivo sugerido para I2V no LTX (Prevenção de VRAM OOM)
        if model == "ltx" and preset == "fast" and req.image_base64:
            if req.duration > 2:
                return {
                    "status": "error", 
                    "error_type": "invalid_duration",
                    "message": f"Modo FAST I2V suporta no máximo 2s. Use modo PRO para durações maiores."
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
            
        # Spawn assíncrono para evitar o limite de 150s do Modal HTTP Gateway
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
                    # Se não terminou, cai no TimeoutError e envia um espaço (heartbeat)
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
            while True:
                try:
                    res = await fc.get.aio(timeout=5.0)
                    # res é bytes de áudio. Devemos retornar em base64.
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
                    if not req.use_upscale:
                        print("[Router Multipass] use_upscale=False — retornando imagem base sem upscale.")
                        yield json.dumps(res) + "\n"
                    else:
                        try:
                            yield " \n"
                            upscale_engine = UniversalComfyEngine()
                            
                            with open(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\flux_upscale_ultrasharp.json", "r", encoding="utf-8") as f:
                                upscale_json = f.read()
                            
                            upscale_job = upscale_engine.generate.spawn(
                                workflow_json_string=upscale_json,
                                prompt=req.base_prompt,
                                input_image_b64=res["image_base64"],
                                is_upscale=True,
                                denoise=0.25
                            )
                            upscale_fc = FunctionCall.from_id(upscale_job.object_id)
                            while True:
                                try:
                                    up_res = await upscale_fc.get.aio(timeout=5.0)
                                    yield json.dumps(up_res) + "\n"
                                    break
                                except TimeoutError:
                                    yield " \n"
                                except Exception as e:
                                    yield json.dumps({"status": "error", "message": f"Erro na Modal (Upscale Multipass): {str(e)}"}) + "\n"
                                    break
                        except Exception as e:
                            yield json.dumps({"status": "error", "message": f"Erro no Roteamento Upscale Multipass: {str(e)}"}) + "\n"
                else:
                    yield json.dumps(res) + "\n"
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                yield json.dumps({"status": "error", "message": f"Erro interno Multipass: {str(e)}", "trace": error_trace}) + "\n"
                    
        return StreamingResponse(stream_result(), media_type="application/x-ndjson")
    except Exception as e:
        return {"status": "error", "message": f"Erro de roteamento Multipass: {str(e)}"}

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
