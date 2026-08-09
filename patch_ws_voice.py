import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

search = '@app.websocket("/ws/jobs/{job_id}")'

replace = '''from fastapi import WebSocket, WebSocketDisconnect
import asyncio

@app.websocket("/ws/voice")
async def ws_voice(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive()
            if "text" in message:
                import json
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "set_voice":
                        print("Voz selecionada no WebSocket:", data.get("voice"))
                        await websocket.send_text(json.dumps({"type": "state", "status": "online", "tool": "Voice updated"}))
                except:
                    pass
            elif "bytes" in message:
                # Mock: Echo back a tiny beep or just ignore to not break frontend
                # Ideally here we'd send to Groq -> LLM -> /api/voice/generate -> send back Blob
                # For now, let's just log and acknowledge to prevent 1006
                pass
    except WebSocketDisconnect:
        print("Live Voice Chat Client Disconnected")

@app.websocket("/ws/jobs/{job_id}")'''

if search in content:
    content = content.replace(search, replace)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Sucesso!")
else:
    print("Falha ao localizar string no servidor_web.py")
