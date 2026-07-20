import subprocess
import logging
import os

logger = logging.getLogger("FFmpegEngine")

class FFmpegEngine:
    def __init__(self):
        self.ffmpeg_cmd = "ffmpeg"
        
    def check_ffmpeg(self):
        try:
            subprocess.run([self.ffmpeg_cmd, "-version"], capture_output=True, check=True)
            return True
        except Exception:
            return False

    async def render_static_video(self, image_path: str, audio_path: str, output_path: str) -> bool:
        """
        Gera um vídeo juntando uma imagem estática e um áudio.
        Para a versão Dark, depois aplicaremos Ken Burns e legendas via ASS.
        """
        logger.info(f"[FFmpeg] Iniciando renderização: {output_path}")
        
        if not os.path.exists(image_path):
            logger.error(f"[FFmpeg] Imagem não encontrada: {image_path}")
            return False
            
        if not os.path.exists(audio_path):
            logger.error(f"[FFmpeg] Áudio não encontrado: {audio_path}")
            return False

        # Comando simples: -loop 1 na imagem, até o tamanho do áudio (-shortest)
        cmd = [
            self.ffmpeg_cmd,
            "-y", # Overwrite
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]
        
        try:
            # Usamos subprocess.Popen ou run para executar
            # O ideal em async é usar asyncio.create_subprocess_exec
            import asyncio
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"[FFmpeg] ✅ Renderização concluída: {output_path}")
                return True
            else:
                logger.error(f"[FFmpeg] ❌ Erro do FFmpeg: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"[FFmpeg] ❌ Falha catastrófica: {e}")
            return False

ffmpeg_engine = FFmpegEngine()

if __name__ == "__main__":
    # Teste rápido
    import asyncio
    async def test():
        if ffmpeg_engine.check_ffmpeg():
            print("FFmpeg disponível!")
        else:
            print("FFmpeg não encontrado.")
    asyncio.run(test())
