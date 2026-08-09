"""
Motor de TTS (Text-to-Speech) via GPU na Modal
===============================================
Utiliza Kokoro TTS (Ultra-rápido, ~50ms latência)
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import io

# Definição da Imagem e Dependências
tts_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "espeak-ng")
    .pip_install(
        "kokoro>=0.3.4",
        "soundfile",
        "torch>=2.0.0",
        "transformers",
        "scipy",
        "fastapi[standard]"
    )
)

with tts_image.imports():
    from fastapi import Request
    from fastapi.responses import StreamingResponse
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline
    
@app.cls(
    image=tts_image,
    gpu="L4",
    timeout=300,
    min_containers=1,
    enable_memory_snapshot=True,
)
class KokoroTTS:
    @modal.enter()
    def load_model(self):
        import torch
        print("Preloading Kokoro TTS model (pt-BR)...")
        if not torch.cuda.is_available():
            print("Snapshot Build: Instantiating on CPU to force cache download...")
            _ = KPipeline(lang_code='p')
            print("Model weights successfully downloaded and cached in RAM!")
        self.pipeline = None

    @modal.method()
    def synthesize_audio(self, text: str, voice: str = "pf_dora") -> bytes:
        if self.pipeline is None:
            print("First request: Instantiating KPipeline on GPU...")
            self.pipeline = KPipeline(lang_code='p')
            
        # p_dora, p_lucas, etc. are Portuguese voices in Kokoro
        try:
            generator = self.pipeline(
                text, voice=voice, 
                speed=1.0, split_pattern=r'\n+'
            )
            
            all_audio = []
            for i, (gs, ps, audio) in enumerate(generator):
                all_audio.append(audio)
            
            if not all_audio:
                raise ValueError("No audio generated")
                
            final_audio = np.concatenate(all_audio)
            
            # Convert to WAV bytes in memory
            buffer = io.BytesIO()
            sf.write(buffer, final_audio, 24000, format='WAV')
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            print(f"Error in TTS generation: {e}")
            raise

@app.function(image=tts_image)
@modal.fastapi_endpoint(method="POST", label="apollo-api-tts")
async def api_tts(request: Request):
    try:
        from fastapi.responses import Response, JSONResponse
        
        # Pode receber json
        data = await request.json()
        text = data.get("text", "")
        voice = data.get("voice", "pf_dora")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        tts_service = KokoroTTS()
        audio_bytes = tts_service.synthesize_audio.remote(text, voice)
        
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
