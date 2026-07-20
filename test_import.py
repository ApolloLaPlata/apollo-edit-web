import sys
import traceback
sys.path.insert(0, r'E:\MEUS PROGRAMAS\TUTORIAL DAS COISAS CODIGOS')
try:
    from config_manager import ConfigManager
    from tts_manager import TTSManager
    from aba_tts import AbaGeracaoTTS
    from media_adjuster import AbaAjustadorMidia
    from aba_inferencia_video import AbaInferenciaVideo
    print('Tudo importado com sucesso no Tutorial das Coisas!')
except Exception as e:
    print('Erro:')
    traceback.print_exc()
