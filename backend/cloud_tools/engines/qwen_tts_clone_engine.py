import modal
import base64
import time
import io
import os
from backend.cloud_tools.engines.universal_engine import apollo_volume

from backend.cloud_tools.tts_app import app

qwen_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("soundfile", "scipy", "librosa", "hf-transfer")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .pip_install("torch==2.4.0", "torchvision==0.19.0", "torchaudio==2.4.0", extra_options="--extra-index-url https://download.pytorch.org/whl/cu121")
    .pip_install("qwen-tts", "transformers", "accelerate")
)

@app.cls(image=qwen_image, gpu="A10G", timeout=600, volumes={"/apollo_volume": apollo_volume})
class QwenTtsCloneEngine:
    @modal.enter()
    def load_model(self):
        print("[QwenTtsCloneEngine] Baixando/Carregando os pesos do Qwen3-TTS-1.7B-Base...")
        import torch
        from qwen_tts import Qwen3TTSModel
        
        t0 = time.time()
        self.model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-1.7B-Base", 
            torch_dtype=torch.bfloat16,
            device_map="cuda:0"
        )
        print(f"[QwenTtsCloneEngine] Modelo Base carregado na GPU em {time.time() - t0:.2f} segundos!")

    @modal.method()
    def inspect_design(self):
        import inspect as py_inspect
        from qwen_tts import Qwen3TTSModel
        res = ""
        if hasattr(Qwen3TTSModel, "generate_voice_design"):
            res += "\n\nINSPECIONAR generate_voice_design:\n" + str(py_inspect.signature(Qwen3TTSModel.generate_voice_design))
            if Qwen3TTSModel.generate_voice_design.__doc__:
                res += "\n" + str(Qwen3TTSModel.generate_voice_design.__doc__)
        return res

    @modal.method()
    def clone(self, text: str, ref_audio_b64: str, ref_text: str, language: str = "portuguese", instruct: str = "", temperature: float = 1.0) -> dict:
        print(f"[QwenTtsCloneEngine] Iniciando clonagem (Language: {language}, Instruct: {instruct}, Temp: {temperature})...")
        t0 = time.time()
        import soundfile as sf
        import traceback
        import tempfile
        
        try:
            # Salvar ref_audio temporariamente
            audio_bytes = base64.b64decode(ref_audio_b64)
            tmp_path = tempfile.mktemp(suffix=".wav")
            with open(tmp_path, "wb") as f:
                f.write(audio_bytes)
                
            kwargs = {"temperature": temperature}
            if instruct:
                kwargs["instruct"] = instruct

            wavs, sr = self.model.generate_voice_clone(
                text=text,
                language=language,
                ref_audio=tmp_path,
                ref_text=ref_text,
                **kwargs
            )
            
            # Limpar arquivo temp
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            buffer = io.BytesIO()
            sf.write(buffer, wavs[0], sr, format='WAV')
            out_bytes = buffer.getvalue()
            b64_out = base64.b64encode(out_bytes).decode("utf-8")
            
            return {
                "status": "success",
                "audio_base64": b64_out,
                "render_time_seconds": round(time.time() - t0, 2)
            }
            
        except Exception as e:
            err = traceback.format_exc()
            return {"status": "error", "message": str(e), "traceback": err}

from fastapi import Request
@app.function(image=qwen_image)
@modal.fastapi_endpoint(method='POST', label='apollo-api-qwen-tts')
async def api_qwen_tts(request: Request):
    try:
        from fastapi.responses import Response, JSONResponse
        import base64
        data = await request.json()
        text = data.get('text', '')
        ref_b64 = data.get('reference_audio_base64', '')
        ref_text = data.get('reference_text', ' ')
        instruct = data.get('instruct', '')
        temperature = data.get('temperature', 1.8)
        language = data.get('language', 'Portuguese')
        
        if not text:
            return JSONResponse({'error': 'No text provided'}, status_code=400)
            
        if ref_b64 and not ref_text.strip():
            print("[QWEN AUTO-STT] Texto de referência vazio, acionando transcrição Whisper...")
            from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT
            stt = WhisperTurboSTT()
            transcription = stt.transcribe.remote(base64.b64decode(ref_b64), "pt")
            ref_text = transcription.get("text", " ")
            print(f"[QWEN AUTO-STT] Transcrição gerada com sucesso: {ref_text}")

        tts_service = QwenTtsCloneEngine()
        result = tts_service.clone.remote(
            text=text, 
            ref_audio_b64=ref_b64, 
            ref_text=ref_text,
            language=language,
            instruct=instruct,
            temperature=temperature
        )
        
        if result['status'] == 'success':
            audio_bytes = base64.b64decode(result['audio_base64'])
            return Response(content=audio_bytes, media_type='audio/wav')
        else:
            return JSONResponse({'error': result['message']}, status_code=500)
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse({'error': str(e)}, status_code=500)
