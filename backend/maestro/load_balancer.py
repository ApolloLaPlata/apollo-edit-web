import os
import json
import uuid
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

from backend.maestro.lightning_fleet import LightningFleetManager

app = FastAPI(title="Apollo Load Balancer - Porta 8000")

# Instancia o gerenciador de frota
fleet = LightningFleetManager()

class RouteRequest(BaseModel):
    model: str
    prompt: str
    job_id: str

def determine_tier(model: str) -> str:
    """Roteador inteligente simples: mapeia modelo para tier."""
    model_lower = model.lower()
    
    if model_lower == "ffmpeg_test":
        return "cpu_free"
    elif model_lower in ["tts_native", "voice_clone", "stable_diffusion"]:
        return "gpu_medium"
    elif model_lower == "flux_pro":
        return "gpu_high"
    else:
        return "cpu_free"

def run_headless_inference(studio_name: str, req: RouteRequest) -> str:
    """
    Acorda a máquina, executa a inferência via SSH, e desliga a máquina.
    """
    print(f"[{req.job_id}] 1. Acordando a máquina '{studio_name}'...")
    fleet.start_node(studio_name)
    
    # Como é um teste de estrutura (Mecanismo), validaremos que a máquina correta acorda,
    # gera um arquivo de mídia compatível usando o FFmpeg instalado na nuvem, e devolve pra cá.
    safe_prompt = req.prompt.replace("'", "").replace('"', '')[:100]
    
    if req.model == "ffmpeg_test":
        output_filename = f"video_{req.job_id}.mp4"
        remote_path = f"/home/zeus/{output_filename}"
        ssh_command = (
            f"ffmpeg -f lavfi -i smptehdbars=duration=2:size=1280x720:rate=30 "
            f"-vf \"drawtext=text='Apollo FFmpeg CPU Free: {safe_prompt}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2\" "
            f"-c:v libx264 -preset ultrafast -y {remote_path}"
        )
    elif req.model in ["tts_native", "voice_clone"]:
        output_filename = f"audio_{req.job_id}.mp3"
        remote_path = f"/home/zeus/{output_filename}"
        ssh_command = (
            f"ffmpeg -f lavfi -i sine=frequency=440:duration=3 -c:a libmp3lame -y {remote_path}"
        )
    elif req.model in ["stable_diffusion", "flux_pro"]:
        output_filename = f"image_{req.job_id}.jpg"
        remote_path = f"/home/zeus/{output_filename}"
        ssh_command = (
            f"ffmpeg -f lavfi -i color=c=blue:s=1024x1024 -vframes 1 "
            f"-vf \"drawtext=text='Apollo {req.model.upper()}: {safe_prompt}':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2\" "
            f"-y {remote_path}"
        )
    else:
        output_filename = f"output_{req.job_id}.mp4"
        remote_path = f"/home/zeus/{output_filename}"
        ssh_command = f"echo 'ok' > {remote_path}"

    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_outputs", output_filename)
    
    try:
        stdout = fleet.run_task_with_timeout(studio_name, ssh_command, timeout_seconds=300)
        print(f"[{req.job_id}] Tarefa remota concluída.")
        
        print(f"[{req.job_id}] 3. Baixando resultado ({output_filename}) via SCP...")
        success = fleet.download_file(studio_name, remote_path, local_path)
        
        if not success:
            raise Exception("Falha ao baixar arquivo via SCP.")
            
        print(f"[{req.job_id}] 4. Limpeza da nuvem (Vassoura)...")
        fleet.run_task(studio_name, f"rm -f {remote_path}")

        print(f"[{req.job_id}] 5. Desligando máquina para economizar dólares...")
        fleet.stop_node(studio_name)
        
        # Para demonstração no frontend, hospedaremos esse arquivo via o Gateway.
        # Aqui no Load Balancer apenas devolvemos um path genérico ou URL do CDN futuro.
        # Por enquanto, assumimos que o arquivo será acessível na pasta estática do Maestro.
        return f"/media/{output_filename}"
        
    except Exception as e:
        print(f"[{req.job_id}] ERRO: {e}")
        print(f"[{req.job_id}] Forçando desligamento de segurança da máquina...")
        fleet.stop_node(studio_name)
        raise e

@app.post("/route")
async def route_job(req: RouteRequest):
    print(f"[{req.job_id}] Nova requisição recebida no Load Balancer! Modelo: {req.model}")
    
    tier = determine_tier(req.model)
    print(f"[{req.job_id}] Tier alocado: {tier}")
    
    try:
        studio_name = fleet.get_node_for_tier(tier)
        print(f"[{req.job_id}] Studio escalado: {studio_name}")
        
        # Inicia a execução pesada
        file_url = run_headless_inference(studio_name, req)
        
        return {
            "status": "success",
            "job_id": req.job_id,
            "data": {
                "file_url": file_url,
                "message": "Gerado e baixado com sucesso da nuvem Lightning!"
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("="*50)
    print("APOLLO LOAD BALANCER INICIADO (PORTA 8000)")
    print("="*50)
    uvicorn.run(app, host="127.0.0.1", port=8000)
