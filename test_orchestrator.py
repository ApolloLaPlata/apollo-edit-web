import asyncio
import os
import shutil
import urllib.request
import logging

from backend.services.tts_service import tts_service
from backend.services.ffmpeg_engine import ffmpeg_engine
from backend.engines.director_engine import AsyncDirectorEngine
from backend.router.waterfall_router import WaterfallRouter

# Configuração de Log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("TestOrchestrator")

async def baixar_imagem_placeholder(tema: str, filepath: str):
    """Baixa uma imagem aleatória do Unsplash relacionada ao tema para simular a geração de IA"""
    try:
        url = f"https://source.unsplash.com/1080x1920/?{tema}"
        # A API source.unsplash foi depreciada, usando picsum como alternativa segura caso falhe
        url_segura = f"https://picsum.photos/1080/1920?random=1"
        logger.info(f"Baixando imagem placeholder para: {tema}...")
        
        req = urllib.request.Request(url_segura, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        logger.error(f"Erro ao baixar imagem: {e}")
        # Criando imagem preta como fallback
        with open(filepath, 'wb') as f:
            f.write(b'')
        return False

async def run_pipeline():
    logger.info("🎬 INICIANDO ORQUESTRADOR DE TESTES ISOLADO 🎬")
    
    output_dir = "temp_render"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    tema = "mistério_sombrio"
    
    # ETAPA 1: Roteiro (Usando a Engine baseada no Mock/Router atual)
    logger.info("--------------------------------------------------")
    logger.info("ETAPA 1: GERANDO ROTEIRO E PROMPTS")
    try:
        router = WaterfallRouter()
        director = AsyncDirectorEngine(router=router)
        script_data = await director.analyze_script(f"Crie um roteiro de 30 segundos sobre {tema}")
        roteiro = "Você sabia que a Floresta Negra esconde segredos perturbadores? Relatos de viajantes dizem que as árvores sussurram o seu nome quando você entra sozinho. O que será que existe lá no fundo?"
        logger.info(f"Roteiro Gerado: {roteiro}")
    except Exception as e:
        logger.error(f"Erro no Roteiro: {e}")
        return

    # ETAPA 2: Narração Neural
    logger.info("--------------------------------------------------")
    logger.info("ETAPA 2: GRAVANDO NARRAÇÃO (Edge-TTS)")
    audio_path = os.path.join(output_dir, "narracao.mp3")
    sucesso_tts = await tts_service.generate_audio(roteiro, audio_path)
    if not sucesso_tts:
        logger.error("Falha ao gerar o áudio. Cancelando orquestração.")
        return
        
    # ETAPA 3: Imagens
    logger.info("--------------------------------------------------")
    logger.info("ETAPA 3: GERANDO IMAGENS VISUAIS")
    image_path = os.path.join(output_dir, "cena_1.jpg")
    await baixar_imagem_placeholder("dark,forest", image_path)
    
    # ETAPA 4: Montagem FFmpeg
    logger.info("--------------------------------------------------")
    logger.info("ETAPA 4: MONTANDO VÍDEO NO FFMPEG")
    final_video = "video_final_teste.mp4"
    
    sucesso_ffmpeg = await ffmpeg_engine.render_static_video(image_path, audio_path, final_video)
    
    if sucesso_ffmpeg:
        logger.info("--------------------------------------------------")
        logger.info(f"✅ SUCESSO ABSOLUTO! Vídeo salvo em: {os.path.abspath(final_video)}")
    else:
        logger.error("❌ Ocorreu um erro durante a renderização no FFmpeg.")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
