import sys
import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace the entire @app.websocket("/ws/voice") function
pattern = re.compile(r'@app\.websocket\("/ws/voice"\)\nasync def ws_voice\(websocket: WebSocket\):.*?except WebSocketDisconnect:\n        print\("\[WS\] Live Voice Chat Client Disconnected"\)\n', re.DOTALL)

replacement = '''@app.websocket("/ws/voice")
async def ws_voice(websocket: WebSocket, channel: str = "default"):
    await websocket.accept()
    
    current_generation_task = None
    voice_config = {"voice_name": "default"}
    
    async def run_llm_and_tts(user_text):
        from backend.cloud_tools.engines.f5_engine import F5TTSEngine
        import os
        import httpx
        
        try:
            f5 = F5TTSEngine()
            
            # Buscar contexto do canal (ex: admin_config.json -> api_config/canais ou similar)
            from config_manager import ConfigManager
            cm = ConfigManager(os.path.join(os.path.dirname(__file__), "config.json"))
            channel_cfg = cm.get(channel, {})
            contexto = channel_cfg.get("channel_context", "")
            
            system_prompt = f"Você é a IA de comunicação em tempo real do canal '{channel}' do Apollo Edit Web. Fale em português do brasil com um tom muito natural e humano. Responda SEMPRE de forma ultra curta e rápida, em no máximo 1 ou 2 frases curtas, para manter a conversa fluida e não gastar tempo. {contexto}"
            
            # Carrega uma voz de referência padrão caso exista
            ref_bytes = b""
            if os.path.exists("default_voice.wav"):
                with open("default_voice.wav", "rb") as f:
                    ref_bytes = f.read()
            elif os.path.exists("web_ui/assets/peter_parker.wav"): # Fallback
                with open("web_ui/assets/peter_parker.wav", "rb") as f:
                    ref_bytes = f.read()
                    
            # CHAMA O LIGHTNING AI PROXY INTERNO INVES DO VLLM
            proxy_url = "http://127.0.0.1:8080/api/lightning_proxy"
            async with httpx.AsyncClient() as client:
                resp = await client.post(proxy_url, json={
                    "model": "nvidia-nemotron-3-ultra-550b-a55b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ]
                }, timeout=30)
                
                if resp.status_code == 200:
                    data = resp.json()
                    full_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # Envia em pequenos pedaços (simulando stream para o TTS)
                    import textwrap
                    chunks = textwrap.wrap(full_text, 80)
                    for chunk in chunks:
                        await websocket.send_text(json.dumps({"type": "llm_chunk", "text": chunk}))
                        if ref_bytes:
                            audio_chunk = await f5.generate_voice.remote.aio(chunk, ref_bytes)
                            await websocket.send_bytes(audio_chunk)
                else:
                    await websocket.send_text(json.dumps({"type": "error", "message": "Lightning falhou"}))
                    
        except asyncio.CancelledError:
            print(f"[WS] Geração interrompida (Task Cancelada) no canal {channel}")
        except Exception as e:
            print(f"[WS] Erro no pipeline Lightning/TTS: {e}")
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    try:
        while True:
            message = await websocket.receive()
            
            if "text" in message:
                import json
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "voice_config":
                        voice_config["voice_name"] = data.get("voice_name", "default")
                        await websocket.send_text(json.dumps({"type": "state", "status": "online", "tool": "Voice updated"}))
                    elif data.get("type") == "vad_interrupt":
                        if current_generation_task and not current_generation_task.done():
                            print("[WS] VAD Interrupt. Cortando...")
                            current_generation_task.cancel()
                except Exception:
                    pass
            elif "bytes" in message:
                # Recebe audio do usuario
                audio_data = message["bytes"]
                from backend.cloud_tools.engines.qwen_stt_engine import SenseVoiceSTTEngine
                try:
                    stt = SenseVoiceSTTEngine()
                    text = await stt.transcribe_audio.remote.aio(audio_data)
                    if text and text.strip():
                        print(f"[WS Usuário - Canal {channel}]: {text}")
                        if current_generation_task and not current_generation_task.done():
                            current_generation_task.cancel()
                        await websocket.send_text(json.dumps({"type": "transcript", "text": text}))
                        current_generation_task = asyncio.create_task(run_llm_and_tts(text))
                except Exception as e:
                    print(f"[WS] Erro de ASR: {e}")
    except WebSocketDisconnect:
        print(f"[WS] Client Disconnected do canal {channel}")
'''

if pattern.search(content):
    content = pattern.sub(replacement, content, count=1)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("WS VOICE SUBSTITUIDO COM SUCESSO E VLLM REMOVIDO.")
else:
    print("WS VOICE NAO ENCONTRADO.")
