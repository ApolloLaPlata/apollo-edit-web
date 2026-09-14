import re
with open("servidor_web.py", "r", encoding="utf-8") as f:
    text = f.read()

# Add AUDIO_JOBS dict
if "AUDIO_JOBS =" not in text:
    text = text.replace('app = FastAPI(title="Apollo Studio Web Engine")', 'app = FastAPI(title="Apollo Studio Web Engine")\n\nAUDIO_JOBS = {}')

# Find the def audio_generate
match = re.search(r'@app\.post\("/api/audio/generate"\).*?async def audio_generate\(req: Request\):.*?try:.*?payload = {.*?}.*?print.*?async with httpx.AsyncClient\(timeout=1200\.0\) as client:(.*?)return {"success": True, "file_url": "/temp/" \+ filename}', text, re.DOTALL)
if match:
    old_block = match.group(0)
    
    # We will replace it with an async task
    new_block = """@app.post("/api/audio/generate")
async def audio_generate(req: Request):
    try:
        body = await req.json()
        prompt = body.get("prompt")
        engine = body.get("engine", "acestep")
        duration = body.get("duration", 30)
        
        # Destino travado na Conta 9 (radiodarktrap) para os Modelos de MÃºsica!
        modal_url = "https://radiodarktrap--apollo-render-router-apollo-api.modal.run/generate/audio_lab"
        
        import httpx
        import uuid
        import os
        import asyncio
        
        model_map = {
            "acestep": "ace-step",
            "sa3": "sa3",
            "minimax": "minimax"
        }
        
        lyrics = body.get("lyrics", "")
        model_mapped = model_map.get(engine, engine)
        
        # --- INJEÃ‡ÃƒO DE MASTERIZAÃ‡ÃƒO E IDIOMA (O SEGREDO DO "PERFEITO") ---
        final_prompt = prompt
        final_lyrics = lyrics
        
        if model_mapped == "ace-step":
            if final_lyrics and "[pt]" not in final_lyrics.lower() and "[en]" not in final_lyrics.lower():
                final_lyrics = "[pt]\\n\\n" + final_lyrics
            if "high quality" not in final_prompt.lower():
                final_prompt += ", high quality, studio mix, masterpiece, hi-fi, wide stereo"
                
        elif model_mapped == "minimax":
            if "language:" not in final_prompt.lower():
                final_prompt = "[Language: Portuguese (Brazil)] [Accent: Brazilian] " + final_prompt
                if final_lyrics and "[pt-br]" not in final_lyrics.lower():
                    final_lyrics = "[PT-BR]\\n" + final_lyrics
            if "studio mix" not in final_prompt.lower():
                final_prompt += ", high quality studio mix, cinematic"
                
        elif model_mapped == "sa3":
            if "masterpiece" not in final_prompt.lower():
                final_prompt += ", high quality, 4k audio, high fidelity, clean, sharp, stereo, masterpiece"

        payload = {
            "model": model_mapped,
            "prompt": final_prompt,
            "lyrics": final_lyrics,
            "duration": float(duration)
        }
        
        job_id = str(uuid.uuid4())
        AUDIO_JOBS[job_id] = {"status": "queued", "job_id": job_id}
        
        async def run_modal_audio_task():
            print(f"[Audio Generator] Solicitando {engine} na conta radiodarktrap para job {job_id}...")
            try:
                async with httpx.AsyncClient(timeout=1200.0) as client:
                    resp = await client.post(modal_url, json=payload)
                    resp.raise_for_status()
                    
                    import base64
                    import json
                    lines = [line for line in resp.text.split('\\n') if line.strip()]
                    last_json = json.loads(lines[-1])
                    audio_b64 = last_json.get('audio_base64')
                    
                    if not audio_b64:
                        AUDIO_JOBS[job_id] = {"status": "error", "error": "Resposta invÃ¡lida da nuvem (sem Ã¡udio)"}
                        return
                        
                    audio_data = base64.b64decode(audio_b64)
                    
                    if not os.path.exists("temp"):
                        os.makedirs("temp")
                    filename = f"{uuid.uuid4().hex}.mp3"
                    filepath = os.path.join("temp", filename)
                    with open(filepath, "wb") as f:
                        f.write(audio_data)
                    
                    AUDIO_JOBS[job_id] = {"status": "success", "file_url": "/temp/" + filename, "success": True}
            except Exception as e:
                AUDIO_JOBS[job_id] = {"status": "error", "error": str(e)}
                
        asyncio.create_task(run_modal_audio_task())
        return {"status": "queued", "job_id": job_id}"""

    text = text.replace(old_block, new_block)

# Also add the status route
status_route = """
@app.get("/api/audio/status/{job_id}")
async def get_audio_status(job_id: str):
    job = AUDIO_JOBS.get(job_id)
    if not job:
        return {"status": "error", "error": "Job not found"}
    return job
"""
if "@app.get(\"/api/audio/status/" not in text:
    text += status_route

with open("servidor_web.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated servidor_web.py with Async Polling!")
