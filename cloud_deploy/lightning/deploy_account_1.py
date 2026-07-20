import os
import subprocess

print("==================================================")
print("🚀 APOLLO DEPLOYER - LIGHTNING CONTA 1")
print("==================================================")

script_dir = os.path.dirname(os.path.abspath(__file__))
fleet_script = os.path.join(script_dir, "deploy_lightning_fleet.py")

print("Executando módulo mestre da frota Lightning (Foco na Conta 1)...")
# O script da frota varre as contas. Para execução individual, podemos apenas
# chamar a frota ou implementar um filtro (por hora, chamamos o gerenciador global).
subprocess.run(["python", fleet_script], cwd=script_dir)
