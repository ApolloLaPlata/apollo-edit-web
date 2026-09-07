import modal

chat_tts_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "ffmpeg")
    .pip_install("torch", "torchaudio", "transformers", "vector_quantize_pytorch", "vocos", "omegaconf", "pydantic", "fastapi", "huggingface_hub", "requests", "tqdm", "soundfile")
    .run_commands("pip install git+https://github.com/2noise/ChatTTS")
    .env({"HF_HOME": "/models/huggingface_cache"})
)

try:
    from backend.cloud_tools.modal_app import app
except ImportError:
    app = modal.App("apollo-api-chattts", image=chat_tts_image)

vol = modal.Volume.from_name("apollo-voice-models", create_if_missing=True)

@app.cls(gpu="L4", scaledown_window=120, image=chat_tts_image, volumes={"/models": vol})
class ChatTTSEngine:
    @modal.enter()
    def setup(self):
        import ChatTTS
        print("Initializing ChatTTS...")
        self.chat = ChatTTS.Chat()
        self.chat.load(compile=False)
        print("ChatTTS ready!")

    @modal.method()
    def generate_audio(self, text: str, temperature: float = 0.3, refine_prompt: str = "") -> bytes:
        import torch
        import soundfile as sf
        import tempfile
        import os
        
        print(f"Gerando áudio para o texto: {text} | Temp: {temperature} | Prompt: {refine_prompt}")
        
        params_refine_text = {'prompt': refine_prompt} if refine_prompt else {}
        params_infer_code = {'temperature': temperature}
        
        wavs = self.chat.infer([text], use_decoder=True, params_refine_text=params_refine_text, params_infer_code=params_infer_code)
        audio_tensor = torch.from_numpy(wavs[0])
        
        temp_wav = tempfile.mktemp(suffix=".wav")
        audio_data = audio_tensor.squeeze().numpy()
        sf.write(temp_wav, audio_data, 24000)
        
        with open(temp_wav, "rb") as f:
            audio_bytes = f.read()
            
        os.remove(temp_wav)
        return audio_bytes
