import whisper
import warnings
warnings.filterwarnings('ignore')

print('Carregando modelo Whisper...')
model = whisper.load_model('base')
print('Transcrevendo...')
result = model.transcribe('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/default_voice.wav')
print('Transcrição:', result['text'])
