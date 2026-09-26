import asyncio
import httpx

async def test_tts_models():
    models_to_test = ['XTTS', 'Qwen-TTS', 'F5-TTS', 'Moss-TTS']
    url = 'http://127.0.0.1:8000/api/studio/modal/eleven_lab'
    for model in models_to_test:
        print(f'Testando {model}...')
        payload = {
            'model': model,
            'text': 'Ola, este e um teste de audio executado pelo sistema automatico do Antigravity.',
            'voice_name': 'female_clean_ref',
            'instruct': 'Fale com muita alegria e animacao',
            'ref_text': 'Ola, eu sou a voz feminina de referencia.'
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    ctype = res.headers.get('content-type')
                    print(f'{model} - SUCESSO. Content: {ctype}, Size: {len(res.content)} bytes')
                else:
                    print(f'{model} - ERRO. Code: {res.status_code}, Detalhe: {res.text}')
        except Exception as e:
            print(f'{model} - FALHA: {e}')

asyncio.run(test_tts_models())
