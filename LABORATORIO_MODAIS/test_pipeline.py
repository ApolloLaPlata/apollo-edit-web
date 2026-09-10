import os
from backend.pipeline.orchestrator import Orchestrator

def main():
    print("=== Iniciando Teste do Orquestrador SaaS B2C ===")
    
    # Vamos usar as chaves do amigo bahia apenas como dummy (ou não, já que é mock o script final por enquanto)
    # Se fosse pra chamar voz real, precisaríamos do b64 e ref_text corretos.
    # Para evitar gastar GPU atoa num dry run, podemos comentar a geração de voz ou passar mock.
    
    orchestrator = Orchestrator()
    print("Módulos carregados com sucesso. O esqueleto está pronto!")

if __name__ == "__main__":
    main()
