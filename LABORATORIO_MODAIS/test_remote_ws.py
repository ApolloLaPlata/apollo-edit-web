import asyncio
import websockets
import json

async def test():
    uri = "wss://api.apolloedit.com/ws/voice?channel=default"
    print("Conectando a:", uri)
    try:
        async with websockets.connect(uri) as ws:
            payload = json.dumps({"type": "user_text", "text": "oi"})
            await ws.send(payload)
            print("Enviado. Aguardando respostas...")
            
            for _ in range(5):
                msg = await ws.recv()
                if isinstance(msg, str):
                    print("Recebido:", msg)
                else:
                    print("Recebido audio chunk bytes")
    except Exception as e:
        print("Erro de conexao:", e)

asyncio.run(test())
