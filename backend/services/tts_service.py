import asyncio
import logging
import os
import edge_tts

logger = logging.getLogger("TTSEngine")

class TTSService:
    def __init__(self, voice="pt-BR-AntonioNeural"):
        self.default_voice = voice
        
    async def generate_audio(self, text: str, output_filepath: str, voice: str = None) -> bool:
        """
        Gera um arquivo de áudio MP3 a partir do texto usando o Edge-TTS da Microsoft.
        100% Gratuito e de alta qualidade (vozes neurais).
        """
        selected_voice = voice or self.default_voice
        logger.info(f"[TTS] Gerando áudio com a voz '{selected_voice}': {text[:50]}...")
        
        try:
            communicate = edge_tts.Communicate(text, selected_voice)
            await communicate.save(output_filepath)
            
            if os.path.exists(output_filepath):
                logger.info(f"[TTS] ✅ Áudio gerado com sucesso: {output_filepath}")
                return True
            else:
                logger.error("[TTS] Falha ao salvar o arquivo de áudio.")
                return False
                
        except Exception as e:
            logger.error(f"[TTS] ❌ Erro crítico ao gerar áudio: {e}")
            return False

tts_service = TTSService()

if __name__ == "__main__":
    # Teste rápido local
    async def test():
        success = await tts_service.generate_audio(
            "Olá, este é um teste do motor neural do Apollo. Bem-vindo à nova era.",
            "test_output.mp3"
        )
        print("Sucesso:", success)
        
    asyncio.run(test())
