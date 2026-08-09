import modal
from backend.cloud_tools.engines.melo_engine import melo_image, MeloTTSEngine, app

@app.local_entrypoint()
def test_melo():
    print('Testando MeloTTS...')
    engine = MeloTTSEngine()
    audio_bytes = engine.generate_voice.remote('Ola, este e um teste do motor Melo TTS.')
    if audio_bytes:
        with open('test_melo.wav', 'wb') as f:
            f.write(audio_bytes)
        print('Teste concluido com sucesso. Audio salvo em test_melo.wav')
    else:
        print('Falha ao gerar audio.')

