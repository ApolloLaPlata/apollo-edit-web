"""
Motor TTS MeloTTS (MyShell)
======================================
Extremamente rápido para uso ao vivo (Live Chat).
Não faz clonagem Zero-Shot, usa vozes embutidas.
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import io

# Definição do Ambiente
melo_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install(
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "git+https://github.com/myshell-ai/MeloTTS.git",
        "soundfile",
        "fastapi[standard]",
        "setuptools<70.0.0"
    )
    .run_commands("python -m unidic download")
)

@app.cls(image=melo_image, gpu="T4", timeout=300, scaledown_window=30, min_containers=0)
class MeloTTSEngine:
    @modal.enter()
    def load_model(self):
        import torch
        from melo.api import TTS
        
        print("[INIT] Carregando MeloTTS na VRAM...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Inicializando o modelo PT (Português)
        self.model = TTS(language='PT', device=self.device)
        self.speaker_ids = self.model.hps.data.spk2id
        print("[INIT] MeloTTS Pronto para Geração!")

    @modal.method()
    def generate_voice(self, text: str):
        """
        Gera áudio a partir do texto usando a voz PT padrão.
        """
        import soundfile as sf
        import os
        
        print(f"[GEN] Recebido pedido MeloTTS. Texto: {text[:50]}...")
        
        try:
            # Geração
            # Pegamos o primeiro speaker disponível para a linguagem
            spk_id = list(self.speaker_ids.values())[0]
            
            # MeloTTS gera diretamente em um arquivo, vamos criar um temp
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
                
            self.model.tts_to_file(text, spk_id, tmp_path, speed=1.0)
            
            with open(tmp_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                
            return audio_bytes
        finally:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)


from fastapi import Request

@app.function(image=melo_image)
@modal.fastapi_endpoint(method="POST", label="apollo-api-melo")
async def api_melo(request: Request):
    try:
        from fastapi.responses import Response, JSONResponse
        
        data = await request.json()
        text = data.get("text", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        tts_service = MeloTTSEngine()
        audio_bytes = tts_service.generate_voice.remote(text)
        
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
