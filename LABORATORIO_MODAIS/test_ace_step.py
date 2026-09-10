import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_comfy_engine import AceStepComfyEngine

def main():
    print("Iniciando AceStepComfyEngine para teste isolado...")
    try:
        with app.run():
            engine = AceStepComfyEngine()
            workflow_mock = "{}"
            print("Spawnando o método load_model e aguardando...")
            res = engine.generate.remote(workflow_mock)
            print("Resultado do motor:", res)
    except Exception as e:
        print("ERRO CAPTURADO NO BOOT DA MODAL:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
