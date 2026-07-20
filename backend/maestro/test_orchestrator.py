import os
import sys
import time
import subprocess
from dotenv import load_dotenv

# Force utf-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

from lightning_sdk.api.teamspace_api import TeamspaceApi
from lightning_sdk.api.studio_api import StudioApi
from lightning_sdk.machine import Machine

load_dotenv()

STUDIO_NAME = "zygomorphic-green-9lz"
SSH_HOST = "s_01ktknr1yes0p125rmtn83519n@ssh.lightning.ai"

def main():
    print("--------------------------------------------------")
    print("INICIANDO ORQUESTRACAO REMOTA - MODO RAW API")
    print(f"Alvo: {STUDIO_NAME}")
    print("--------------------------------------------------")

    team_api = TeamspaceApi()
    studio_api = StudioApi()

    print("Buscando a maquina na sua conta...")
    teamspaces = team_api.list_teamspaces(os.getenv("LIGHTNING_USER_ID"))

    target_studio = None
    target_team = None

    for ts in teamspaces:
        try:
            s = studio_api.get_studio(STUDIO_NAME, ts.id)
            if s:
                target_studio = s
                target_team = ts
                break
        except Exception:
            pass

    if not target_studio:
        print("Maquina nao encontrada!")
        return

    print(f"Encontrada! ID: {target_studio.id} | Teamspace: {target_team.name}")

    status = studio_api.get_studio_status(target_studio.id, target_team.id)
    # The status is an internal enum or object in the SDK, we stringify it
    status_str = str(status).lower()
    print(f"Status atual: [{status_str}]")

    # The API might return an Enum or similar. E.g., StudioStatus.STOPPED
    if "running" not in status_str:
        print("Ligando os motores do Studio via API Direta (isso pode levar uns 2 minutos)...")
        # Start the studio
        # Notice we use target_studio.machine, which is string, we pass to Machine.from_str
        studio_api.start_studio(target_studio.id, target_team.id, Machine.CPU)
        
        while True:
            status = studio_api.get_studio_status(target_studio.id, target_team.id)
            status_str = str(status).lower()
            print(f"Atualizando status... [{status_str}]")
            if "running" in status_str:
                break
            time.sleep(10)

    print("MAQUINA ONLINE!")
    print("Aguardando 10 segundos extras pro SSH carregar...")
    time.sleep(10)

    print("Iniciando renderizacao via SSH direto...")
    ffmpeg_cmd = "ffmpeg -f lavfi -i smptehdbars=duration=4:size=1280x720:rate=30 -vf \"drawtext=text='PROVA FINAL APOLLO':fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2\" -c:v libx264 -preset ultrafast -y PROVA_FINAL.mp4"
    
    subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", SSH_HOST, ffmpeg_cmd])

    print("Baixando arquivo PROVA_FINAL.mp4...")
    subprocess.run(["scp", "-o", "StrictHostKeyChecking=no", f"{SSH_HOST}:PROVA_FINAL.mp4", "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\PROVA_FINAL.mp4"])
    print("Download concluido!")

    print("Desligando a maquina para economizar gasolina...")
    studio_api.stop_studio(target_studio.id, target_team.id)
    print("Maquina dormindo.")
    print("--------------------------------------------------")
    print("DEU CERTO!")

if __name__ == "__main__":
    main()
