import os
import json
import httpx
import uuid
import asyncio
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Response
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
import hashlib

global_modal_semaphore = asyncio.Semaphore(2)

router = APIRouter(prefix="/api/studio/modal", tags=["Studio Modal Proxy"])

DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cloud_tools", "cloud_accounts_db.json"))

JOBS = {}

def get_active_modal_account():
    if not os.path.exists(DB_FILE):
        return None
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            accounts = json.load(f)
        except:
            return None
    for acc in accounts:
        if acc.get("provider") == "modal" and acc.get("is_active"):
            return acc
    return None

async def process_modal_job(job_id: str, method: str, url: str, headers: dict, body: bytes):
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
            try:
                content = response.json()
            except:
                content = response.text
                
            JOBS[job_id] = {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "content": content
            }
        except Exception as e:
            JOBS[job_id] = {
                "status": "error",
                "status_code": 500,
                "content": {"error": str(e)}
            }

@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(status_code=200, content=JOBS[job_id])

@router.api_route("/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_to_modal(path: str, request: Request, background_tasks: BackgroundTasks):
    if request.method == "OPTIONS":
        return JSONResponse(status_code=200, content={"status": "ok"})
    
    # --- INTERNAL LOCK (BOT PROTECTION) ---
    expected_lock = os.environ.get("APOLLO_SECRET_LOCK", "apollo-beta-key-2026")
    client_lock = request.headers.get("x-apollo-lock")
    if client_lock != expected_lock:
        raise HTTPException(status_code=401, detail="Unauthorized access. Bot protection is active.")
    # --------------------------------------
    
    acc = get_active_modal_account()
    if not acc:
        raise HTTPException(status_code=503, detail="Nenhuma conta Modal ativa configurada na Colmeia.")
        
    workspace = acc.get("workspace")
    if not workspace:
        raise HTTPException(status_code=500, detail="Workspace modal nao configurado.")

    remote_path = path
    if path == "generate_image":
        remote_path = "generate/image"
    elif path == "generate_video":
        remote_path = "generate/video"
    elif path == "generate_universal":
        remote_path = "generate/universal"
    elif path == "generate_tts":
        remote_path = "generate/tts"
        
    modal_url = f"https://{workspace}--apollo-render-router-apollo-api.modal.run/{remote_path}"
    print(f"[PROXY DEBUG] Routing to: {modal_url}", flush=True)
    
    headers = {}
    if acc.get("proxy_secret"):
        headers["Authorization"] = f"Bearer {acc.get('proxy_secret')}"
    
    if "content-type" in request.headers:
        headers["Content-Type"] = request.headers["content-type"]
            
    body = await request.body()
    
    # --- INTERCEPT QWEN MULTI-PASS FOR LLM LIGHTNING ---
    if remote_path == "generate/image":
        try:
            req_json = json.loads(body.decode("utf-8"))
            images_b64 = req_json.get("reference_images_base64", [])
            if req_json.get("model") == "qwen-image" and images_b64 and len(images_b64) >= 1 and not req_json.get("dynamic_steps"):
                num_imgs = len(images_b64)
                print(f"[PROXY DEBUG] Detectado Qwen com {num_imgs} imagens. Acionando LLM estrutural...", flush=True)
                
                admin_cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "admin_config.json"))
                lit_key = ""
                if os.path.exists(admin_cfg_path):
                    with open(admin_cfg_path, 'r', encoding='utf-8') as f:
                        c = json.load(f)
                        keys = c.get("api_config", {}).get("lightning_chat", {}).get("api_keys", [])
                        if keys:
                            lit_key = keys[0]
                
                if lit_key:
                    import modal
                    import asyncio
                    import hashlib
                    import json
                    
                    vision_descriptions = []
                    cache_file = os.path.join(os.path.dirname(__file__), "vision_cache.json")
                    
                    try:
                        cache_data = {}
                        if os.path.exists(cache_file):
                            with open(cache_file, "r", encoding="utf-8") as cf:
                                cache_data = json.load(cf)
                                
                        for idx, b64 in enumerate(images_b64):
                            img_hash = hashlib.sha256(b64[:10000].encode('utf-8')).hexdigest()
                            if img_hash in cache_data:
                                vision_descriptions.append(f"Image {idx}: {cache_data[img_hash]}")
                                print(f"[PROXY DEBUG] Imagem {idx} lida do cache.", flush=True)
                            else:
                                def call_vision(img_b64=b64):
                                    engine = modal.Cls.lookup("apollo-vision-engine", "FlorenceVisionEngine")
                                    return engine().analyze_image.remote(img_b64)
                                print(f"[PROXY DEBUG] Chamando Vision Engine para Imagem {idx}...", flush=True)
                                desc = await asyncio.to_thread(call_vision)
                                cache_data[img_hash] = desc
                                vision_descriptions.append(f"Image {idx}: {desc}")
                                
                        with open(cache_file, "w", encoding="utf-8") as cf:
                            json.dump(cache_data, cf)
                            
                    except Exception as ve:
                        print(f"[PROXY DEBUG] Erro Vision Engine: {ve}", flush=True)
                        vision_descriptions.append("Fallback: Error analyzing images.")
                        
                    combined_vision = "\\n".join(vision_descriptions)
                    
                    llm_prompt = f"""You are an expert AI prompt engineer for Qwen 2.5 Image Edit.
The user provided {num_imgs} reference images. Raw prompt: "{req_json.get('prompt')}"

Our Vision AI analyzed the images:
{combined_vision}

Task: Rewrite the user's prompt into a highly detailed, descriptive prompt suitable for Qwen.
Rules:
1. Describe the final scene clearly in English. Do NOT copy exact poses if the user requested a NEW scene.
2. If {num_imgs} == 1: Add "SINGLE CHARACTER ONLY, NO CLONES, DO NOT REPEAT".
3. If {num_imgs} > 1: It is a Multi-Pass! Group the images into sequential logical steps (max 2 images per pass).
   - Pass 1 (Base scene): "prompt": "Create a scene... Add the character from Image 0..."
   - Pass 2+ (Editing): "prompt": "EDIT THIS SCENE. Keep existing elements exactly as they are. Add the character from Image 1..."
4. Generate an intelligent "negative_prompt" to exclude things the user DOES NOT want.
5. Output ONLY a valid JSON array of objects. Each object must have: "prompt" (string), "negative_prompt" (string, optional), "image_indices" (array of ints).
Make sure ALL {num_imgs} indices are used. No markdown blocks."""

                    async with httpx.AsyncClient(timeout=45.0) as lc:
                        llm_success = False
                        for k in keys:
                            try:
                                llm_res = await lc.post(
                                    "https://lightning.ai/api/v1/chat/completions",
                                    headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"},
                                    json={
                                        "model": "nvidia-nemotron-3-ultra-550b-a55b",
                                        "messages": [{"role": "user", "content": llm_prompt}]
                                    }
                                )
                                if llm_res.status_code == 200:
                                    llm_success = True
                                    res_content = llm_res.json()["choices"][0]["message"]["content"]
                                    s_idx = res_content.find('[')
                                    e_idx = res_content.rfind(']')
                                    if s_idx != -1 and e_idx != -1:
                                        dynamic_steps = json.loads(res_content[s_idx:e_idx+1])
                                        req_json["dynamic_steps"] = dynamic_steps
                                        if len(dynamic_steps) > 0 and "negative_prompt" in dynamic_steps[0]:
                                            req_json["negative_prompt"] = dynamic_steps[0]["negative_prompt"]
                                        
                                        body = json.dumps(req_json).encode("utf-8")
                                        print(f"[PROXY DEBUG] LLM Dynamic Steps: {dynamic_steps}", flush=True)
                                    break
                            except Exception as ex:
                                print(f"[PROXY DEBUG] Excecao na chave: {ex}", flush=True)
                        
        except Exception as e:
            print(f"[PROXY DEBUG] Erro ao injetar LLM: {e}", flush=True)
    # ---------------------------------------------------

    # Execucao com Streaming para repassar heartbeats e evitar 504 no Nginx
    print(f"[PROXY DEBUG] [RATE LIMIT] Aguardando liberacao na fila da Modal (Max 2 simultaneos)...", flush=True)
    async with global_modal_semaphore:
        print(f"[PROXY DEBUG] [RATE LIMIT] Fila liberada! Enviando requisicao para a Modal.", flush=True)
        client = httpx.AsyncClient(timeout=300.0)
        try:
            req = client.build_request(
                method=request.method,
                url=modal_url,
                headers=headers,
                content=body
            )
            response = await client.send(req, stream=True)
            
            async def stream_gen():
                try:
                    async for chunk in response.aiter_raw():
                        yield chunk
                finally:
                    await response.aclose()
                    await client.aclose()
                    
            return StreamingResponse(
                stream_gen(),
                status_code=response.status_code,
                media_type=response.headers.get("content-type", "application/json")
            )
        except Exception as e:
            await client.aclose()
            raise HTTPException(status_code=500, detail=str(e))









