import re
import uuid

with open('apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ADD AUDIO JOBS DICT
if 'audio_jobs = {}' not in content:
    content = content.replace('app = FastAPI(', 'audio_jobs = {}\napp = FastAPI(')

# REWRITE /api/audio/generate
new_code = '''@app.post("/api/audio/generate")
async def audio_generate(req: Request):
    try:
        body = await req.json()
        prompt = body.get("prompt")
        engine = body.get("engine", "acestep")
        duration = body.get("duration", 30)
        
        job_id = str(uuid.uuid4())
        audio_jobs[job_id] = {"status": "processing"}
        
        import asyncio
        asyncio.create_task(process_audio_background(job_id, prompt, engine, duration))
        
        return {"status": "queued", "job_id": job_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def process_audio_background(job_id, prompt, engine, duration):
    try:
        modal_url = "https://radiodarktrap--apollo-render-router-apollo-api.modal.run/generate/audio_lab"
        import httpx
        import uuid
        import os
        
        model_map = {
            "acestep": "ace-step",
            "sa3": "sa3",
            "minimax": "minimax"
        }
        
        payload = {
            "model": model_map.get(engine, engine),
            "prompt": prompt,
            "duration": float(duration)
        }
        
        print(f"[Audio Generator] Solicitando {engine} na conta radiodarktrap para job {job_id}...")
        async with httpx.AsyncClient(timeout=1200.0) as client:
            resp = await client.post(modal_url, json=payload)
            resp.raise_for_status()
            
            import base64
            import json
            lines = [line for line in resp.text.split('\\n') if line.strip()]
            last_json = json.loads(lines[-1])
            audio_b64 = last_json.get('audio_base64')
            
            if not audio_b64:
                audio_jobs[job_id] = {"status": "error", "error": f"Modal falhou: {last_json.get('error', 'Sem áudio')}"}
                return
                
            audio_data = base64.b64decode(audio_b64)
            
            os.makedirs("/home/ubuntu/apollo_edit/media/audio_lab", exist_ok=True)
            filename = f"audio_{uuid.uuid4().hex[:8]}.mp3"
            filepath = f"/home/ubuntu/apollo_edit/media/audio_lab/{filename}"
            with open(filepath, "wb") as f:
                f.write(audio_data)
            
            audio_jobs[job_id] = {"status": "success", "file_url": f"/media/audio_lab/{filename}"}
    except Exception as e:
        audio_jobs[job_id] = {"status": "error", "error": str(e)}

@app.get("/api/audio/status/{job_id}")
async def audio_status(job_id: str):
    return audio_jobs.get(job_id, {"status": "error", "error": "Job não encontrado"})
'''

# We need to replace the old @app.post("/api/audio/generate") completely.
# Let's find it.
import re
match = re.search(r'@app\.post\("/api/audio/generate"\).*?(?=\n@app\.)', content, re.DOTALL)
if match:
    content = content.replace(match.group(0), new_code + "\n")
else:
    print("Could not find /api/audio/generate to replace!")

with open('apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(content)
