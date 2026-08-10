import whisper
import warnings
warnings.filterwarnings('ignore')

model = whisper.load_model('base')
print('Transcrevendo teste_kokoro.wav...')
r1 = model.transcribe('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/teste_kokoro.wav')
print('Kokoro:', r1['text'])

print('Transcrevendo test_moss.wav...')
r2 = model.transcribe('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/test_moss.wav')
print('Moss:', r2['text'])
