import json
import os
import subprocess
import time

DB_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\cloud_accounts_db.json"
MODAL_ENGINE_DIR = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\cloud_deploy\modal"
MODAL_ENGINE_SCRIPT = "apollo_modal_engine.py"

def deploy_all():
    print("==================================================")
    print("🚀 APOLLO FLEET DEPLOYER - INICIANDO...")
    print("==================================================")
    
    with open(DB_PATH, "r", encoding="utf-8") as f:
        accounts = json.load(f)
        
    modal_accounts = [acc for acc in accounts if acc.get("provider") == "modal"]
    
    for i, acc in enumerate(modal_accounts):
        print(f"\n[{i+1}/{len(modal_accounts)}] Padronizando Conta: {acc['name']} ({acc['workspace']})")
        
        # Seta as variáveis de ambiente para a CLI da Modal autenticar via Token
        env = os.environ.copy()
        env["MODAL_TOKEN_ID"] = acc["token_id"]
        env["MODAL_TOKEN_SECRET"] = acc["token_secret"]
        
        # 1. Download/Cache dos Modelos
        print(f" -> [1/2] Pulando download pesado (modelos ja cacheados)...")
        # try:
        #     res_dl = subprocess.run(
        #         ["modal", "run", f"{MODAL_ENGINE_SCRIPT}::download_ai_models"],
        #         cwd=MODAL_ENGINE_DIR,
        #         env=env,
        #         encoding="utf-8"
        #     )
        #     if res_dl.returncode != 0:
        #         print(f" ⚠️ Aviso/Erro no Download: Código {res_dl.returncode}")
        #     else:
        #         print(" ✅ Modelos cacheados com sucesso!")
        # except Exception as e:
        #      print(f" ❌ Falha crítica no passo de download: {e}")
             
        # 2. Deploy do Motor
        print(f" -> [2/2] Impondo a arquitetura mestre (Deploy)...")
        try:
            res_dep = subprocess.run(
                ["modal", "deploy", MODAL_ENGINE_SCRIPT],
                cwd=MODAL_ENGINE_DIR,
                env=env,
                encoding="utf-8"
            )
            if res_dep.returncode != 0:
                print(f" ⚠️ Aviso/Erro no Deploy: Código {res_dep.returncode}")
            else:
                print(" ✅ Deploy finalizado e online!")
        except Exception as e:
            print(f" ❌ Falha crítica no passo de deploy: {e}")
            
        print("--------------------------------------------------")
        
if __name__ == "__main__":
    deploy_all()
    print("\n✅ Implantação em massa finalizada!")
