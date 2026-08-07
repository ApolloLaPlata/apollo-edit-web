"""
Motor de Clonagem de Voz F5-TTS
======================================
Utiliza arquitetura Flow Matching.
Excelente para Zero-Shot em PT-BR.
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import io

# Definição do Ambiente
f5_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "f5-tts",
        "soundfile",
        "fastapi[standard]",
        "setuptools"
    )
)

@app.cls(image=f5_image, gpu="L4", timeout=600, scaledown_window=31, min_containers=0)
class F5TTSEngine:
    @modal.enter()
    def load_model(self):
        import torch
        from huggingface_hub import hf_hub_download
        from f5_tts.api import F5TTS
        
        print("[INIT] Baixando/Carregando F5-TTS Base na VRAM...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Inicia o modelo oficial F5-TTS v1 Base (Suporte multilingue)
        self.f5 = F5TTS(device=self.device)
        print("[INIT] F5-TTS Pronto para Geração!")

    @modal.method()
    def generate_voice(self, text: str, reference_audio_bytes: bytes = None):
        """
        Gera áudio a partir do texto. Zero-shot se referência for fornecida.
        """
        import soundfile as sf
        import tempfile
        import os
        
        print(f"[GEN] Recebido pedido F5-TTS. Texto: {text[:50]}...")
        
        ref_file_path = None
        ref_text = "" # F5 infere sozinho ou a gente não passa texto de ref
        
        if reference_audio_bytes:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(reference_audio_bytes)
                ref_file_path = f.name
                
        try:
            if not ref_file_path:
                raise ValueError("F5-TTS requires a reference audio to clone. None provided.")
                
            # A API Python do F5TTS.infer espera ref_file, ref_text, e gen_text
            wav, sr, spect = self.f5.infer(
                ref_file=ref_file_path,
                ref_text=ref_text,
                gen_text=text
            )
            
            # Converter para bytes WAV
            out_io = io.BytesIO()
            sf.write(out_io, wav, samplerate=sr, format='WAV')
            return out_io.getvalue()
        finally:
            if ref_file_path and os.path.exists(ref_file_path):
                os.remove(ref_file_path)


from fastapi import Request

@app.function(image=f5_image)
@modal.fastapi_endpoint(method="POST", label="apollo-api-f5-tts")
async def api_f5_tts(request: Request):
    try:
        from fastapi.responses import Response, JSONResponse
        import base64
        
        data = await request.json()
        text = data.get("text", "")
        ref_b64 = data.get("ref_audio_base64", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        ref_bytes = base64.b64decode(ref_b64) if ref_b64 else None
            
        tts_service = F5TTSEngine()
        audio_bytes = tts_service.generate_voice.remote(text, ref_bytes)
        
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
