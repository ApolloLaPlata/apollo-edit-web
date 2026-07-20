import asyncio
import os
import sys
import logging
from httpx import AsyncClient, ASGITransport

# Adicionar raiz do projeto ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("E2ETest")

async def run_e2e_tests():
    logger.info("🚀 Iniciando Simulação E2E do Motor 3.0...")

    # Gerar um arquivo de áudio de mentira (silêncio total de 2 segundos) para testar o FFmpeg
    dummy_audio_path = os.path.join(os.path.dirname(__file__), "test_audio.wav")
    os.system(f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 2 -q:a 9 -acodec pcm_s16le "{dummy_audio_path}" >nul 2>&1')

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # TESTE 1: Director Engine (Waterfall Router + LLM)
        logger.info("🧪 Teste 1: Director Engine (Análise Semântica)")
        payload_director = {
            "script_text": "O Ibovespa fechou em alta hoje com as novas medidas econômicas."
        }
        res1 = await client.post("/render/analyze_script", json=payload_director)
        if res1.status_code == 200:
            logger.info(f"✅ Sucesso! Resposta: {res1.json()}")
        else:
            logger.error(f"❌ Falha no Teste 1: {res1.text}")

        # TESTE 2: Audio Engine (FFmpeg em background)
        logger.info("🧪 Teste 2: Audio Engine (Limpeza de Silêncio FFmpeg)")
        if os.path.exists(dummy_audio_path):
            payload_audio = {
                "audio_path": dummy_audio_path,
                "noise_level": "-40dB"
            }
            res2 = await client.post("/render/clean_audio", json=payload_audio)
            if res2.status_code == 200:
                logger.info(f"✅ Sucesso! Resposta: {res2.json()}")
            else:
                logger.error(f"❌ Falha no Teste 2: {res2.text}")
        else:
            logger.error("❌ FFmpeg dummy áudio não criado, verifique se o ffmpeg está no PATH.")

        # TESTE 3: Video Engine (Render Timeline Subprocess)
        logger.info("🧪 Teste 3: Video Engine (Disparo de Subprocesso de Render)")
        dummy_timeline = {
            "clips": [],
            "transitions": [],
            "draft_mode": True
        }
        res3 = await client.post("/render/start_video", json={"timeline_data": dummy_timeline})
        if res3.status_code == 200:
            data3 = res3.json()
            logger.info(f"✅ Sucesso no Start! Job ID: {data3['job_id']}")
            
            # Polling para ver se o status muda
            job_id = data3['job_id']
            await asyncio.sleep(2)
            res_status = await client.get(f"/render/status_video/{job_id}")
            logger.info(f"✅ Status do Vídeo: {res_status.json()}")
        else:
            logger.error(f"❌ Falha no Teste 3: {res3.text}")

    # Limpeza
    if os.path.exists(dummy_audio_path):
        os.remove(dummy_audio_path)
    
    logger.info("🏁 Testes E2E Concluídos.")

if __name__ == "__main__":
    asyncio.run(run_e2e_tests())
