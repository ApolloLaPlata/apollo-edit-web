import asyncio
import websockets
import json
import traceback

async def test_ws():
    uri = 'ws://127.0.0.1:8080/ws/voice'
    try:
        async with websockets.connect(uri) as websocket:
            # Mandando payload invalido para LLM
            payload = {'type': 'user_text', 'text': {'ola': 123}}
            await websocket.send(json.dumps(payload))
            while True:
                response = await websocket.recv()
                print('Recebeu:', response)
                data = json.loads(response)
                if data.get('type') == 'error':
                    break
    except Exception as e:
        print("Erro WS:", str(e))

asyncio.run(test_ws())
