import modal

if __name__ == "__main__":
    import subprocess
    print("Iniciando download dos pesos do MiniMax na Modal (Volume persistente)...")
    subprocess.check_call(["modal", "run", "backend.cloud_tools.engines.minimax_engine::download_minimax"])
    print("Download finalizado!")