from backend.cloud_tools.engines.qwen_tts_engine import QwenTtsEngine
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def run():
    print("Iniciando inspeção...")
    engine = QwenTtsEngine()
    res = engine.inspect_api.remote()
    print("======== RESULTADO ========")
    print(res)
