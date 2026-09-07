import modal
import os
import time

from backend.cloud_tools.modal_app import app
volume = modal.Volume.from_name("apollo-models", create_if_missing=True)

image = modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.11") \
    .apt_install("git", "ffmpeg") \
    .pip_install("torch", "torchaudio", "torchvision", extra_options="--index-url https://download.pytorch.org/whl/cu121") \
    .pip_install("transformers", "accelerate", "soundfile", "git+https://github.com/huggingface/diffusers@dafe3733fcfdbf3c48915fe77be3aef65b5d6a2d", "sentencepiece", "huggingface_hub", "fastapi", "pydantic", "requests")

@app.cls(gpu="a100", timeout=3600, image=image, volumes={"/models": volume})
class MinimaxEngine:
    @modal.enter()
    def setup(self):
        import torch
        from diffusers import ModularPipeline
        
        print("[MiniMax] Carregando pesos do Volume...")
        self.pipe = ModularPipeline.from_pretrained(
            "MiniMaxAI/MiniMax-Music3",
            cache_dir="/models/huggingface_cache"
        )
        self.pipe.load_components(dtype=torch.bfloat16)
        self.pipe.to("cuda")
        print("[MiniMax] H100 Pronta!")

    @modal.method()
    def generate(self, prompt: str, is_instrumental: bool = True, lyrics: str = "", duration: float = 240.0):
        import torch
        import soundfile as sf
        import io
        import time

        print(f"[MiniMax] Duracao alvo: {duration}s | Instrumental: {is_instrumental}")
        
        if is_instrumental or not lyrics.strip():
            final_lyrics = "[Instrumental]\n\n[Verse]\n[Instrumental]\n\n[Chorus]\n[Instrumental]\n\n[Bridge]\n[Instrumental]\n\n[Outro]\n[Instrumental]"
        else:
            final_lyrics = lyrics
            
        start = time.time()
        result = self.pipe(
            prompt=prompt,
            lyrics=final_lyrics, 
            audio_duration=duration, 
            generator=torch.Generator("cuda").manual_seed(int(time.time() % 100000))
        )
        audio = getattr(result, "audios", getattr(result, "audio", result))[0]
        
        print(f"[MiniMax] Concluido em {time.time() - start:.2f} segundos!")
        
        buffer = io.BytesIO()
        sf.write(buffer, audio.T, self.pipe.sampling_rate, format='WAV')
        
        return buffer.getvalue()

@app.local_entrypoint()
def run_minimax_test():
    import base64
    engine = MinimaxEngine()
    
    os.makedirs("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    t = {
        "nome": "Vocal_Pro_BR",
        "prompt": "[Language: Portuguese (Brazil)] [Accent: Brazilian/Paulista] Brazilian Trap music, heavy 808 sub bass, aggressive male vocals singing in Brazilian Portuguese, dark ambient pads, 140 BPM, high quality studio mix",
        "lyrics": "[Verse]\n[PT-BR]\nEntrando nas sombras da mente, olha o grave batendo na caixa.\nSem limite pra quem vem de baixo, o suor na camisa nao racha.\n[Chorus]\n[PT-BR]\nO tempo fechou, a noite e nossa!\nNinguem passa do limite, a batida destroca!\n[Verse 2]\n[PT-BR]\nSente o 808 tremendo o chao, Apollo Edit dominando o beat.\nSem recuar, sem pedir perdao, cada rima e um novo hit.\n[Chorus]\n[PT-BR]\nO tempo fechou, a noite e nossa!\nNinguem passa do limite, a batida destroca!\n[Bridge]\n[PT-BR]\nA batida e pesada, o grave destroi.\nO beat e insano, a mente corroe.\n[Chorus]\n[PT-BR]\nO tempo fechou, a noite e nossa!\nNinguem passa do limite, a batida destroca!\n[Outro]\n[PT-BR]\nFade out no grave... Apollo na mente.",
        "is_instrumental": False,
        "duration": 210.0 # 3.5 minutos
    }

    print("Iniciando TESTE VOCAL PRO no MiniMax-Music3 (H100)...")
    print(f"Executando Teste: {t['nome']}")
        
    wav_base64 = engine.generate.remote(
        prompt=t['prompt'], 
        is_instrumental=t['is_instrumental'], 
        lyrics=t['lyrics'], 
        duration=t['duration']
    )
    
    wav_data = base64.b64decode(wav_base64)
    out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_audio/MiniMax_Stress_{t['nome']}_{int(time.time())}.wav"
    
    with open(out_path, "wb") as f:
        f.write(wav_data)
        
    print(f"Salvo em: {out_path}")
