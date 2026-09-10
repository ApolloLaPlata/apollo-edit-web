import asyncio
import websockets
import json

async def test():
    uri = "ws://127.0.0.1:8080/ws/voice?channel=default"
    try:
        async with websockets.connect(uri) as ws:
            payload = json.dumps({"type": "user_text", "text": "oi"})
            await ws.send(payload)
            print("Enviado. Aguardando respostas...")
            
            for _ in range(5):
                msg = await ws.recv()
                print("Recebido:", msg[:200])
                if "error" in msg:
                    break
    except Exception as e:
        print("Erro de conexao:", e)

asyncio.run(test())
