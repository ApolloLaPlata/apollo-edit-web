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
def download_xtts():
    import os
    os.environ["COQUI_TOS_AGREED"] = "1"
    from TTS.api import TTS
    # Fazer o download do modelo para dentro da camada da imagem Docker (bakear o modelo)
    TTS("tts_models/multilingual/multi-dataset/xtts_v2")

xtts_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "torch<2.6.0",
        "torchaudio<2.6.0",
        "TTS==0.22.0",
        "soundfile",
        "fastapi[standard]",
        "numpy<2.0.0",
        "transformers<4.35.0"
    )
    .run_function(download_xtts)
)

xtts_cache = modal.Volume.from_name("xtts-cache", create_if_missing=True)

@app.cls(image=xtts_image, gpu="L4", timeout=600, scaledown_window=30, min_containers=0)
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
    def generate_voice(self, text: str, reference_audio_bytes: bytes = None, temperature: float = 0.75, speed: float = 1.0):
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
            # Geração com parâmetros avançados (Laboratório)
            wav = self.tts.tts(
                text=text, 
                speaker_wav=ref_file_path, 
                language="pt",
                temperature=temperature,
                speed=speed
            )
            
            # Converter para bytes WAV
            out_io = io.BytesIO()
            # O XTTSv2 usa 24000 de samplerate geralmente
            sf.write(out_io, wav, samplerate=24000, format='WAV')
            return out_io.getvalue()
        finally:
            if ref_file_path and os.path.exists(ref_file_path):
                os.remove(ref_file_path)

    @modal.fastapi_endpoint(method="POST", label="apollo-api-xtts")
    async def api_xtts(self, request: dict):
        """
        Endpoint web que funde a requisição HTTP diretamente na GPU (0 hops).
        Recebe JSON com {"text": "...", "ref_audio_base64": "..."}.
        Retorna áudio OGG/Opus.
        """
        import base64
        import subprocess
        from fastapi.responses import Response, JSONResponse
        
        try:
            data = request
            text = data.get("text", "")
            ref_b64 = data.get("ref_audio_base64", "")
            temperature = data.get("temperature", 0.75)
            speed = data.get("speed", 1.0)
            
            if not text:
                return JSONResponse({"error": "No text provided"}, status_code=400)
                
            ref_bytes = base64.b64decode(ref_b64) if ref_b64 else None
            
            # Chama a geração WAV original
            wav_bytes = self.generate_voice.local(text, ref_bytes, temperature, speed)
            
            # Converter WAV para Opus in-memory via FFmpeg
            process = subprocess.Popen(
                ['ffmpeg', '-i', 'pipe:0', '-c:a', 'libopus', '-b:a', '64k', '-vbr', 'on', '-f', 'ogg', 'pipe:1'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            opus_bytes, err = process.communicate(input=wav_bytes)
            
            if process.returncode != 0:
                print("FFmpeg Error:", err.decode('utf-8', errors='ignore'))
                # Fallback to WAV if FFmpeg fails
                return Response(content=wav_bytes, media_type="audio/wav")
            
            return Response(content=opus_bytes, media_type="audio/ogg")
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
