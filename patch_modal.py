import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\apollo_modal_engine.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Insert AudioLabRequest after VideoRequest
req_target = 'class VideoRequest(BaseModel):'
req_replacement = '''class AudioLabRequest(BaseModel):
    prompt: str
    lyrics: Optional[str] = None
    model: str = "sa3" # "sa3", "minimax", "ace-step"
    duration: int = 30
    
class VideoRequest(BaseModel):'''

if 'class AudioLabRequest' not in content:
    content = content.replace(req_target, req_replacement)

# Insert route before @app.function
route_target = '@app.function('
route_replacement = '''@web_app.post("/generate/audio_lab")
def api_generate_audio_lab(req: AudioLabRequest):
    try:
        model = req.model.lower()
        if model == "sa3":
            from backend.cloud_tools.engines.stable_audio_engine import StableAudioEngine
            engine = StableAudioEngine()
            print(f"[Router] Spawning StableAudioEngine for SA3")
            fc = engine.generate.spawn(prompt=req.prompt, seconds=req.duration)
            res = fc.get()
            if isinstance(res, bytes):
                import base64
                b64 = base64.b64encode(res).decode('utf-8')
                return {"status": "success", "audio_base64": b64, "message": "SA3 Recebido!"}
            return {"status": "error", "error_type": "generation_failed", "message": "Erro na geracao SA3"}
            
        elif model == "minimax":
            from backend.cloud_tools.engines.minimax_engine import MinimaxEngine
            engine = MinimaxEngine()
            print(f"[Router] Spawning MinimaxEngine")
            fc = engine.generate_music.spawn(prompt=req.prompt)
            res = fc.get()
            if isinstance(res, bytes):
                import base64
                b64 = base64.b64encode(res).decode('utf-8')
                return {"status": "success", "audio_base64": b64, "message": "MiniMax Recebido!"}
            return {"status": "error", "error_type": "generation_failed", "message": "Erro na geracao MiniMax"}
            
        elif model == "ace-step":
            from backend.cloud_tools.engines.ace_step_python_engine import AceStepPythonEngine
            engine = AceStepPythonEngine()
            print(f"[Router] Spawning AceStepPythonEngine")
            fc = engine.generate.spawn(prompt=req.prompt, lyrics=req.lyrics)
            res = fc.get()
            if isinstance(res, bytes):
                import base64
                b64 = base64.b64encode(res).decode('utf-8')
                return {"status": "success", "audio_base64": b64, "message": "ACE-Step Recebido!"}
            return {"status": "error", "error_type": "generation_failed", "message": "Erro na geracao ACE-Step"}
            
        else:
            return {"status": "error", "error_type": "invalid_model", "message": f"Modelo {model} nao suportado."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "error_type": "exception", "message": str(e)}

@app.function('''

if '@web_app.post("/generate/audio_lab")' not in content:
    content = content.replace(route_target, route_replacement, 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Adicionado Audio Lab no modal engine!")
