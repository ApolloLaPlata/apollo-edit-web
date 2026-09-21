import re

with open('servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace audio_generate signature
new_code = code.replace(
    'async def audio_generate(req: Request):\n    try:\n        body = await req.json()',
    'async def audio_generate(req: Request, background_tasks: BackgroundTasks):\n    try:\n        body = await req.json()\n        import uuid\n        job_id = str(uuid.uuid4())\n        if "AUDIO_JOBS" not in globals():\n            global AUDIO_JOBS\n            AUDIO_JOBS = {}\n        AUDIO_JOBS[job_id] = {"status": "queued"}\n        background_tasks.add_task(run_audio_generate_bg, job_id, body)\n        return {"status": "queued", "job_id": job_id}\n    except Exception as e:\n        return {"success": False, "error": str(e)}\n\nasync def run_audio_generate_bg(job_id: str, body: dict):\n    try:'
)

new_code = new_code.replace(
    'return {"success": True, "file_url": f"/temp/{filename}"}',
    'if "AUDIO_JOBS" in globals():\n                AUDIO_JOBS[job_id] = {"status": "success", "success": True, "file_url": f"/temp/{filename}"}\n            return'
)

new_code = new_code.replace(
    'except Exception as e:\n        print(f"[Audio Generator] Erro: {e}")\n        return {"success": False, "error": str(e)}',
    'except Exception as e:\n        print(f"[Audio Generator] Erro: {e}")\n        if "AUDIO_JOBS" in globals():\n            AUDIO_JOBS[job_id] = {"status": "error", "success": False, "error": str(e)}\n        return'
)

status_endpoint = '''@app.get("/api/audio/status/{job_id}")
async def get_audio_status(job_id: str):
    if "AUDIO_JOBS" not in globals():
        return {"status": "error", "error": "Job system not initialized"}
    job = AUDIO_JOBS.get(job_id)
    if not job:
        return {"status": "error", "error": "Job not found"}
    return job'''

if '@app.get("/api/audio/status/{job_id}")' in new_code:
    start = new_code.find('@app.get("/api/audio/status/{job_id}")')
    end = new_code.find('return job', start) + 10
    new_code = new_code[:start] + status_endpoint + new_code[end:]
else:
    new_code += '\n\n' + status_endpoint

with open('servidor_web_patched.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
