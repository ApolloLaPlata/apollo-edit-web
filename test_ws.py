import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8080/ws/voice?channel=music_factory"
    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado ao WebSocket de voz!")
            
            msg = json.dumps({"type": "text", "text": "OlÃ¡, quem Ã© vocÃª?"})
            await websocket.send(msg)
            
            for i in range(3):
                try:
                    resp = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    if isinstance(resp, str):
                        data = json.loads(resp)
                        if data.get("type") == "llm_chunk":
                            print("CHUNK RECEBIDO:", data["text"])
                        else:
                            print("RESPOSTA RECEBIDA:", data)
                    else:
                        print(f"AUDIO RECEBIDO: {len(resp)} bytes")
                except asyncio.TimeoutError:
                    print("Timeout esperando resposta (30s).")
                    break
    except Exception as e:
        print("Erro de conexÃ£o WS:", e)

asyncio.run(test_ws())
