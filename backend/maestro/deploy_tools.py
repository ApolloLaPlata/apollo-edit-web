import os
import sys
from backend.maestro.lightning_fleet import LightningFleetManager

def deploy_to_all_nodes():
    fleet = LightningFleetManager()
    
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cloud_tools"))
    
    for account in fleet.registry.get("accounts", []):
        for studio in account.get("studios", []):
            studio_name = studio["studio_name"]
            ssh_host = studio["ssh_host"]
            
            # Skip placeholders for now
            if "0000" in ssh_host or "1111" in ssh_host:
                print(f"Skipping placeholder studio {studio_name}...")
                continue
                
            print(f"\n==============================================")
            print(f"Iniciando deploy no nó: {studio_name} ({studio.get('tier')})")
            print(f"==============================================")
            
            try:
                fleet.start_node(studio_name)
                
                print("Criando diretório /home/zeus/apollo_tools/...")
                fleet.run_task(studio_name, "mkdir -p /home/zeus/apollo_tools")
                
                print(f"Fazendo upload dos scripts de {local_dir}...")
                for filename in os.listdir(local_dir):
                    if filename.endswith(".py") or filename == "requirements.txt":
                        local_file = os.path.join(local_dir, filename)
                        remote_file = f"/home/zeus/apollo_tools/{filename}"
                        fleet.upload_file(studio_name, local_file, remote_file)
                        
                print("Instalando dependencias via pip na maquina remota...")
                pip_cmd = "rm -rf ~/.cache && mkdir -p ~/.cache && pip install --break-system-packages -r /home/zeus/apollo_tools/requirements.txt"
                fleet.run_task(studio_name, f"bash -lc '{pip_cmd}'")
                
                print(f"Deploy concluído para {studio_name}!")
            except Exception as e:
                print(f"Falha no deploy para {studio_name}: {e}")

if __name__ == "__main__":
    deploy_to_all_nodes()
