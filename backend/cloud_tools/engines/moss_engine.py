"""
Motor de Clonagem de Voz MOSS-TTS (8B)
======================================
Este motor carrega o modelo OpenMOSS-Team/MOSS-TTS na Modal.
Ele utiliza a arquitetura de 8 Bilhões de Parâmetros e faz download
dos pesos diretamente da HuggingFace.

Exige GPU de alto desempenho (H100 ou A100) devido ao tamanho do modelo (25GB).
"""

import modal
from backend.cloud_tools.modal_app import app
import os
import io

# Definição do Ambiente e Dependências para o MOSS-TTS
moss_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "packaging",
        "ninja",
        "setuptools",
        "wheel",
        "torch>=2.0.0",
        "torchaudio>=2.0.0"
    )
    .pip_install(
        "transformers",
        "safetensors==0.6.2",
        "numpy==2.1.0",
        "orjson==3.11.4",
        "tqdm==4.67.1",
        "PyYAML==6.0.3",
        "einops==0.8.1",
        "scipy==1.16.2",
        "librosa==0.11.0",
        "tiktoken==0.12.0",
        "huggingface_hub",
        "fastapi[standard]",
        "accelerate>=0.26.0"
    )
    .run_commands(
        [
            "python -c \"from huggingface_hub import snapshot_download; "
            "print('[BUILD] Baixando Pesos do MOSS-TTS (25GB)... Isso pode demorar na primeira vez.'); "
            "snapshot_download(repo_id='OpenMOSS-Team/MOSS-TTS', local_dir_use_symlinks=False)\""
        ]
    )
)

@app.cls(image=moss_image, gpu="H100", timeout=600, scaledown_window=30,
 min_containers=0)
class MossTTSEngine:
    @modal.enter()
    def load_model(self):
        import torch
        from transformers import AutoModel, AutoProcessor
        
        print("[INIT] Carregando MOSS-TTS (8B) na VRAM...")
        
        self.device = torch.device("cuda")
        self.dtype = torch.bfloat16
        
        # O trust_remote_code=True é obrigatório porque a arquitetura MossTTSDelay customizada 
        # será baixada e executada diretamente do repositório da HuggingFace.
        model_id = "OpenMOSS-Team/MOSS-TTS"
        
        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
        if hasattr(self.processor, "audio_tokenizer"):
            self.processor.audio_tokenizer = self.processor.audio_tokenizer.to(self.device)
            
        self.model = AutoModel.from_pretrained(
            model_id, 
            trust_remote_code=True, 
            torch_dtype=self.dtype,
            device_map="auto" # Faz o offload inteligente para não dar OOM
        ).eval()
        
        print("[INIT] MOSS-TTS Pronto para Geração!")

    @modal.method()
    def generate_voice(self, text: str, reference_audio_bytes: bytes = None):
        """
        Gera áudio a partir do texto fornecido.
        Se reference_audio_bytes for fornecido, tenta realizar a clonagem zero-shot.
        """
        import torch
        import torchaudio
        import io
        import numpy as np
        import soundfile as sf
        
        print(f"[GEN] Recebido pedido TTS. Texto: {text[:50]}...")
        
        inputs = {"conversations": [{"role": "user", "content": text}]}
        
        if reference_audio_bytes:
            # Carregar o áudio de referência a partir de bytes
            audio_io = io.BytesIO(reference_audio_bytes)
            ref_audio, sr = torchaudio.load(audio_io)
            inputs["reference_audio"] = ref_audio
            inputs["reference_sample_rate"] = sr
            
        with torch.no_grad():
            # A API exata do MOSS-TTS depende da implementação do repositório.
            # Baseado nos scripts padrões da comunidade para o pipeline deles:
            input_features = self.processor(**inputs)
            if hasattr(input_features, "to"):
                input_features = input_features.to(self.device, dtype=self.dtype)
                
            outputs = self.model.generate(**input_features, max_new_tokens=4096)
            messages = self.processor.decode(outputs)
            audio = messages[0].audio_codes_list[0]
            if audio.ndim == 1:
                audio = audio.unsqueeze(0)
            audio_data = audio.detach().cpu().to(torch.float32).numpy()
            
        # Converter para bytes WAV
        out_io = io.BytesIO()
        sf.write(out_io, audio_data.T, samplerate=self.processor.model_config.sampling_rate, format='WAV')
        out_bytes = out_io.getvalue()
        
        return out_bytes

from fastapi import Request

@app.function(image=moss_image)
@modal.fastapi_endpoint(method="POST", label="apollo-api-moss-tts")
async def api_moss_tts(request: Request):
    try:
        from fastapi.responses import Response, JSONResponse
        
        # Pode receber json
        data = await request.json()
        text = data.get("text", "")
        
        if not text:
            return JSONResponse({"error": "No text provided"}, status_code=400)
            
        tts_service = MossTTSEngine()
        # O processamento do moss tts demora, então aguardamos a remote call
        audio_bytes = tts_service.generate_voice.remote(text)
        
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": str(e)}, status_code=500)
