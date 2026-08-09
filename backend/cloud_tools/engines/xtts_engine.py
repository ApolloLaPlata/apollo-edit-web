"""
Motor de Clonagem de Voz XTTSv2 (Coqui)
======================================
Excelente suporte nativo ao PT-BR.
Pesa apenas 1.8GB. Suporta clonagem Zero-Shot.
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import io

# Definição do Ambiente
xtts_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "torch<2.6.0",
        "torchaudio<2.6.0",
        "TTS==0.22.0",
        "soundfile",
        "fastapi[standard]",
        "numpy<2.0.0", # TTS pode ter problemas com numpy 2.0
        "transformers<4.35.0" # XTTSv2 (TTS 0.22) quebra se usar o Transformers atual
    )
)

xtts_cache = modal.Volume.from_name("xtts-cache", create_if_missing=True)

@app.cls(image=xtts_image, gpu="T4", timeout=600, scaledown_window=30, min_containers=0, volumes={"/root/.local/share/tts": xtts_cache})
class XttsEngine:
    @modal.enter()
    def load_model(self):
        import torch
        from TTS.api import TTS
        
        print("[INIT] Carregando XTTSv2 na VRAM...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Concordando com os termos do Coqui (TOS) via variável de ambiente
        os.environ["COQUI_TOS_AGREED"] = "1"
        
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        print("[INIT] XTTSv2 Pronto para Geração!")

    @modal.method()
    def generate_voice(self, text: str, reference_audio_bytes: bytes = None):
        """
        Gera áudio a partir do texto. Requer referência para clonagem.
        Caso contrário, usa uma voz padrão ou precisamos embutir um áudio genérico.
        """
        import soundfile as sf
        import tempfile
        import os
        
        print(f"[GEN] Recebido pedido XTTSv2. Texto: {text[:50]}...")
        
        # XTTSv2 OBRIGA ter um arquivo WAV de referência.
        # Se não fornecido, usaríamos um áudio genérico. 
        # Aqui vamos exigir o áudio por precaução, ou escrever um dummy se None.
        ref_file_path = None
        
        if reference_audio_bytes:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(reference_audio_bytes)
                ref_file_path = f.name
        else:
            # Não tem clonagem solicitada, mas XTTSv2 precisa de um speaker.
            # Idealmente teríamos um áudio base PT-BR embutido, mas para simplificar:
            raise ValueError("XTTSv2 requer um áudio de referência (speaker) obrigatório.")
                
        try:
            # Geração
            wav = self.tts.tts(text=text, speaker_wav=ref_file_path, language="pt")
            
            # Converter para bytes WAV
            out_io = io.BytesIO()
            # O XTTSv2 usa 24000 de samplerate geralmente
            sf.write(out_io, wav, samplerate=24000, format='WAV')
            return out_io.getvalue()
        finally:
            if ref_file_path and os.path.exists(ref_file_path):
                os.remove(ref_file_path)


from fastapi import Request

@app.function(image=xtts_image, timeout=900)
@modal.fastapi_endpoint(method="POST", label="apollo-api-xtts")
async def api_xtts(request: Request):
    try:
        from fastapi.responses import Response, JSONResponse
        
        data = await request.json()
        text = data.get("text", "")
        ref_b64 = data.get("ref_audio_base64", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        import base64
        ref_bytes = base64.b64decode(ref_b64) if ref_b64 else None
            
        tts_service = XttsEngine()
        audio_bytes = tts_service.generate_voice.remote(text, ref_bytes)
        
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
