import modal
from backend.cloud_tools.engines.moss_engine import moss_image, MossTTSEngine, app

@app.local_entrypoint()
def test_moss():
    print('Testando MOSS-TTS (8B)...')
    engine = MossTTSEngine()
    audio_bytes = engine.generate_voice.remote('Ola, este e um teste do motor Moss TTS de 8 bilhoes de parametros.')
    if audio_bytes:
        with open('test_moss.wav', 'wb') as f:
            f.write(audio_bytes)
        print('Teste concluido com sucesso. Audio salvo em test_moss.wav')
    else:
        print('Falha ao gerar audio.')

