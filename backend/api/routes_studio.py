import os
import json
import httpx
import uuid
import asyncio
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Response
from fastapi.responses import JSONResponse, StreamingResponse

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
            if req_json.get("model") == "qwen-image" and images_b64 and len(images_b64) > 1 and not req_json.get("dynamic_steps"):
                num_imgs = len(images_b64)
                print(f"[PROXY DEBUG] Detectado Qwen Multi-Pass com {num_imgs} imagens. Acionando LLM estrutural...", flush=True)
                
                # Load API key from admin_config.json
                admin_cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "admin_config.json"))
                lit_key = ""
                if os.path.exists(admin_cfg_path):
                    with open(admin_cfg_path, 'r', encoding='utf-8') as f:
                        c = json.load(f)
                        keys = c.get("api_config", {}).get("api_keys", [])
                        if keys:
                            lit_key = keys[0]
                
                if lit_key:
                    llm_prompt = f"""You are an expert AI prompt engineer. The user wants to generate an image using an iterative multi-pass process on Qwen.
Global prompt: "{req_json.get('prompt')}"

We have {num_imgs} character reference images, with zero-based indices from 0 to {num_imgs - 1}.
Qwen supports up to 3 image inputs per generation pass. You must group the {num_imgs} images into sequential logical steps to accumulate them into a single final image.
Return ONLY a valid JSON array of objects. Each object must have:
- "prompt": string (The descriptive prompt for this pass. Pass 1 generates the base scene with the first characters. Pass 2+ must start with 'EDIT THIS SCENE. Keep existing elements exactly as they are...' and add the new elements).
- "image_indices": array of integers (Which image indices to use in this pass, max 3 per pass).
Make sure ALL {num_imgs} indices are used across the steps.
Do not include any markdown formatting like ```json."""
                    
                    async with httpx.AsyncClient(timeout=10.0) as lc:
                        llm_res = await lc.post(
                            "https://lightning.ai/api/v1/chat/completions",
                            headers={"Authorization": f"Bearer {lit_key}", "Content-Type": "application/json"},
                            json={
                                "model": "nvidia-nemotron-3-ultra-550b-a55b",
                                "messages": [{"role": "user", "content": llm_prompt}]
                            }
                        )
                        if llm_res.status_code == 200:
                            content = llm_res.json()["choices"][0]["message"]["content"]
                            s_idx = content.find('[')
                            e_idx = content.rfind(']')
                            if s_idx != -1 and e_idx != -1:
                                dynamic_steps = json.loads(content[s_idx:e_idx+1])
                                req_json["dynamic_steps"] = dynamic_steps
                                body = json.dumps(req_json).encode("utf-8")
                                print(f"[PROXY DEBUG] LLM Dynamic Steps Injetados com sucesso: {dynamic_steps}", flush=True)
                        else:
                            print(f"[PROXY DEBUG] Erro no LLM: {llm_res.text}", flush=True)
        except Exception as e:
            print(f"[PROXY DEBUG] Erro ao injetar LLM: {e}", flush=True)
    # ---------------------------------------------------

    # Execucao com Streaming para repassar heartbeats e evitar 504 no Nginx
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

