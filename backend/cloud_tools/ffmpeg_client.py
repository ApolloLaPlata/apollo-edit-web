import os
import sys
import httpx
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from cloud_tools.lightning_manager import watchdog
except ImportError:
    watchdog = None

load_dotenv()
APOLLO_SECRET_KEY = "APOLLO_SECRET_KEY_123"
FFMPEG_STUDIO_NAME = os.getenv("FFMPEG_STUDIO_NAME", "cpu-free")

async def execute_remote_ffmpeg(action: str, payload: dict):
    """
    Função base para enviar uma tarefa pesada de mídia para a máquina CPU na Lightning.
    Acorda a máquina se necessário e envia o payload.
    """
    if watchdog:
        watchdog.wake_up(FFMPEG_STUDIO_NAME)
        
    status = None
    if watchdog:
        status = watchdog.get_status(FFMPEG_STUDIO_NAME)
    
    target_url = "http://localhost:8000/predict"
    if status and "url" in status:
        target_url = f"{status['url']}/predict"
        
    headers = {"Authorization": f"Bearer {APOLLO_SECRET_KEY}"}
    data = {"action": action, **payload}
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(target_url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            if attempt < max_retries - 1:
                import asyncio
                print(f"[FFmpegClient] Falha ao contatar {FFMPEG_STUDIO_NAME}. Tentando novamente em 10s...")
                await asyncio.sleep(10)
            else:
                raise e
