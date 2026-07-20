import os
import json
import subprocess
import time

DB_FILE = os.path.join(os.path.dirname(__file__), "backend", "cloud_tools", "cloud_accounts_db.json")

def deploy_to_all_modal():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        accounts = json.load(f)
    
    modal_accounts = [acc for acc in accounts if acc.get("provider") == "modal"]
    
    for acc in modal_accounts:
        print(f"\n==============================================")
        print(f"Deploying to Modal Workspace: {acc['workspace']} ({acc['name']})")
        print(f"==============================================")
        
        env = os.environ.copy()
        env["MODAL_TOKEN_ID"] = acc["token_id"]
        env["MODAL_TOKEN_SECRET"] = acc["token_secret"]
        env["PYTHONIOENCODING"] = "utf-8"
        
        # O usuário pediu para manter a conta 1 (roxingo) espelhada, mas bloqueada.
        # Nós já deixamos is_active = false no DB para roxingo. Aqui apenas fazemos o deploy.
        
        try:
            subprocess.run(
                ["modal", "deploy", "-m", "backend.cloud_tools.apollo_modal_engine"],
                env=env,
                check=True
            )
            print(f"Deploy concluído com sucesso para {acc['workspace']}!")
        except subprocess.CalledProcessError as e:
            print(f"Falha no deploy para {acc['workspace']}: {e}")
            
if __name__ == "__main__":
    deploy_to_all_modal()
