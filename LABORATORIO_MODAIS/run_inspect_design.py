from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def run():
    print("Iniciando inspeção...")
    engine = QwenTtsCloneEngine()
    res = engine.inspect_design.remote()
    print("======== RESULTADO ========")
    print(res)
