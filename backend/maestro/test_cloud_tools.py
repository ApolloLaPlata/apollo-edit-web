import os
import time
from backend.maestro.lightning_fleet import LightningFleetManager

def run_tests():
    fleet = LightningFleetManager()
    studio_name = "zygomorphic-green-9lz"
    
    print("=== INICIANDO BATERIA DE TESTES NA NUVEM ===")
    
    # Garantir que a maquina esta ligada
    try:
        fleet.start_node(studio_name)
    except Exception as e:
        print(f"Erro ao ligar ou checar maquina: {e}")
        return
        
    print("\n--- Teste 1: Limpeza da Vassoura (Cleanup) ---")
    fleet.cleanup_node(studio_name)
    
    print("\n--- Teste 2: Remocao de Fundo (Rembg) ---")
    # Para rodar isso de verdade precisariamos de um video teste na maquina local
    # Vamos apenas simular a execucao com um dummy file ou um comando basico
    print("Aguardando implementacao do video teste local...")
    
    print("\n--- Teste 3: Geracao de TTS ---")
    test_text = "Esta é uma voz gerada nas nuvens com custo zero de armazenamento!"
    
    # Criar a pasta de jobs primeiro
    fleet.run_task(studio_name, "mkdir -p /home/zeus/apollo_jobs")
    
    remote_out = "/home/zeus/apollo_jobs/teste_tts.mp3"
    
    # Rodar o comando SSH
    cmd = f"python3 /home/zeus/apollo_tools/tool_edge_tts.py '{test_text}' {remote_out}"
    print(f"Comando: {cmd}")
    fleet.run_task(studio_name, cmd)
    
    # Baixar o resultado
    local_out = os.path.join(os.path.dirname(__file__), "teste_tts_baixado.mp3")
    print(f"Baixando resultado para {local_out}...")
    fleet.download_file(studio_name, remote_out, local_out)
    
    if os.path.exists(local_out):
        print(f"SUCESSO! O audio foi baixado com tamanho {os.path.getsize(local_out)} bytes.")
    else:
        print("FALHA: O arquivo não foi baixado.")
        
    print("\n--- Teste 4: Limpeza Pos-Teste ---")
    fleet.cleanup_node(studio_name)
    
    print("Testes concluidos.")

if __name__ == "__main__":
    run_tests()
