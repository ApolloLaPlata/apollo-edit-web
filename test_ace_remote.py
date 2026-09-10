import modal
import sys

def main():
    print("Buscando AceStepComfyEngine na Modal (apollo-render-router)...")
    try:
        engine_cls = modal.Cls.from_name("apollo-render-router", "AceStepComfyEngine")
        engine = engine_cls()
        print("Invocando generate.remote...")
        # Chamando com dict vazio simulando json de workflow pra forçar o boot
        res = engine.generate.remote("{}")
        print("Resultado do boot:", res)
    except Exception as e:
        print("Erro ao acionar a Modal:", str(e))

if __name__ == "__main__":
    main()
