import os
import subprocess
import sys

# Força o Python a rodar em modo silencioso/UTF-8 para evitar os erros do terminal Windows
os.environ["PYTHONUTF8"] = "1"
os.environ["MODAL_LOGLEVEL"] = "WARNING"

print("Iniciando o Deploy da API...")
res_deploy = subprocess.run([sys.executable, "-m", "modal", "deploy", "backend/cloud_tools/apollo_modal_engine.py"], capture_output=True, text=True, encoding="utf-8", errors="replace")
with open("deploy_log.txt", "w", encoding="utf-8") as f:
    f.write("DEPLOY STDOUT:\n" + res_deploy.stdout)
    f.write("\nDEPLOY STDERR:\n" + res_deploy.stderr)

print("\nIniciando o Download do YuE...")
res_run = subprocess.run([sys.executable, "-m", "modal", "run", "download_yue_volume.py"], capture_output=True, text=True, encoding="utf-8", errors="replace")

with open("run_log.txt", "w", encoding="utf-8") as f:
    f.write("RUN STDOUT:\n" + res_run.stdout)
    f.write("\nRUN STDERR:\n" + res_run.stderr)

