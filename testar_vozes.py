import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tts_manager import TTSManager
from config_manager import ConfigManager

def run_tests():
    cfg = ConfigManager()
    tts = TTSManager(cfg)
    texto = "Isso é um teste incrível da nossa capacidade infinita de memória e de clonagem de voz na Modal!"
    
    print("\n=== Iniciando Teste QWEN TTS (Modelo 5) ===")
    tts.generate_audio("Rafael Descargas", texto, "teste_qwen.wav", _modelo_override=5)
    
    print("\n=== Iniciando Teste MOSS TTS (Modelo 2) ===")
    tts.generate_audio("Rafael Descargas", texto, "teste_moss.wav", _modelo_override=2)

if __name__ == "__main__":
    run_tests()
