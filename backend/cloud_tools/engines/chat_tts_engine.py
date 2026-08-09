"""
Motor TTS Focado em Conversação (ChatTTS) via Modal
===================================================
Otimizado para inflexões naturais, risadas e interjeições para o Pocket Director.
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import io
from fastapi import Request

chattts_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "torch>=2.0.0",
        "torchaudio",
        "ChatTTS",
        "soundfile",
        "fastapi",
        "requests"
    )
)

@app.cls(
    image=chattts_image,
    gpu="L4",
    timeout=300,
    min_containers=0,
    enable_memory_snapshot=True,
)
class ConversationalTTS:
    @modal.enter()
    def load_model(self):
        import torch
        print("Preloading ChatTTS...")
        
        if not torch.cuda.is_available():
            print("Snapshot Build: Fazendo download compulsório do ChatTTS para RAM...")
            import ChatTTS
            chat = ChatTTS.Chat()
            chat.load(compile=False, device='cpu') # Força download dos pesos
            print("Pesos do ChatTTS baixados para RAM!")
            
        self.chat = None

    @modal.method()
    def synthesize_audio(self, text: str) -> bytes:
        import ChatTTS
        import soundfile as sf
        import io
        import numpy as np

        if self.chat is None:
            print("First request: Instanciando ChatTTS na GPU...")
            self.chat = ChatTTS.Chat()
            self.chat.load(compile=False, device='cuda')

        # ChatTTS aceita arrays de texto e retorna arrays de audio
        texts = [text]
        wavs = self.chat.infer(texts)
        
        audio_data = wavs[0]
        
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, 24000, format='WAV')
        buffer.seek(0)
        return buffer.read()

@app.function(image=chattts_image)
@modal.fastapi_endpoint(method="POST", label="apollo-api-chat-tts")
async def api_chat_tts(request: Request):
    try:
        from fastapi.responses import Response, JSONResponse
        data = await request.json()
        text = data.get("text", "")
        
        if not text:
            return JSONResponse({"error": "Texto não providenciado"}, status_code=400)
            
        tts_service = ConversationalTTS()
        audio_bytes = await tts_service.synthesize_audio.remote.aio(text)
        
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
