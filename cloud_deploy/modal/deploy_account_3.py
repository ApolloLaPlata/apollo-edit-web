import os
import json
import subprocess

DB_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\cloud_accounts_db.json"
MODAL_ENGINE_DIR = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\cloud_deploy\modal"
MODAL_ENGINE_SCRIPT = "apollo_modal_engine.py"

def deploy_account_3():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        accounts = json.load(f)
        
    modal_accs = [acc for acc in accounts if acc.get("provider") == "modal"]
    if len(modal_accs) < 3:
        print("Erro: Não há 3 contas Modal no DB.")
        return
        
    acc = modal_accs[2] # Account 3
    
    print(f"\n=============================================")
    print(f"🚀 INICIANDO DEPLOY NA CONTA 3: {acc['name']}")
    print(f"=============================================")
    
    env = os.environ.copy()
    env["MODAL_TOKEN_ID"] = acc["token_id"]
    env["MODAL_TOKEN_SECRET"] = acc["token_secret"]
    
    # 1. Download
    print(f" -> [1/2] Baixando modelos de IA para a Conta 3...")
    try:
        res_dl = subprocess.run(
            ["modal", "run", f"{MODAL_ENGINE_SCRIPT}::download_ai_models"],
            cwd=MODAL_ENGINE_DIR,
            env=env,
            encoding="utf-8"
        )
    except Exception as e:
        print(f"Erro: {e}")

    # 2. Deploy
    print(f" -> [2/2] Impondo a arquitetura mestre (Deploy)...")
    try:
        res_dep = subprocess.run(
            ["modal", "deploy", MODAL_ENGINE_SCRIPT],
            cwd=MODAL_ENGINE_DIR,
            env=env,
            encoding="utf-8"
        )
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    deploy_account_3()
