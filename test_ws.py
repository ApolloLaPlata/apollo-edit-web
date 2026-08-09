import asyncio, websockets
async def test():
  async with websockets.connect('wss://api.apolloedit.com.br/ws/voice') as ws:
    print('Connected!')
    await ws.send('{"type": "ping"}')
    print(await ws.recv())
asyncio.run(test())
