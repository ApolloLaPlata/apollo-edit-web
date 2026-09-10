import modal
import os
import time

app = modal.App("minimax-music3-engine")

image = modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.11") \
    .apt_install("git", "ffmpeg") \
    .pip_install("torch", "torchaudio", "torchvision", extra_options="--index-url https://download.pytorch.org/whl/cu121") \
    .pip_install("transformers", "accelerate", "soundfile", "diffusers>=0.30.0", "sentencepiece")

@app.cls(gpu="H100", image=image, timeout=1200)
class MiniMaxEngine:
    @modal.enter()
    def setup(self):
        import torch
        from diffusers import ModularPipeline
        print("Baixando e carregando pesos do MiniMax Music 3 (8B+0.6B+2.4B)...")
        self.pipe = ModularPipeline.from_pretrained("MiniMaxAI/MiniMax-Music3")
        self.pipe.load_components(dtype=torch.bfloat16)
        self.pipe.to("cuda")
        print("Modelos MiniMax carregados na H100!")

    @modal.method()
    def generate(self, prompt: str, lyrics: str):
        import torch
        import soundfile as sf
        import io
        import time

        print(f"Gerando musica cantada (MiniMax) para: {prompt}")
        start = time.time()
        audio = self.pipe(
            prompt=prompt,
            lyrics=lyrics, 
            audio_duration=240.0, 
            generator=torch.Generator("cuda").manual_seed(42),
            output="audios"
        )[0]
        print(f"Gerado em {time.time()-start:.1f} segundos!")
        
        buffer = io.BytesIO()
        sf.write(buffer, audio.T, self.pipe.sampling_rate, format='WAV')
        return buffer.getvalue()

@app.local_entrypoint()
def run_test():
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    engine = MiniMaxEngine()
    prompt = "brazilian trap, aggressive male vocals, deep 808 bass, fast hi-hats, dark ambient pads, 140 BPM, high quality studio mix"
    lyrics = "[Verse]\nENTRANDO NAS SOMBRAS DA MENTE\nOLHA O GRAVE BATENDO NA CAIXA\n[Chorus]\nO TEMPO FECHOU, A NOITE E NOSSA\nNINGUEM PASSA DO LIMITE\n[Verse]\nSENTE O 808 TREMENDO O CHAO\nAPOLLO EDIT DOMINANDO O BEAT"
    print("Iniciando requisição para MiniMax-Music3 na nuvem (H100)...")
    wav_data = engine.generate.remote(prompt, lyrics)
    
    timestamp = int(time.time())
    out_path = f"LABORATORIO_MODAIS/testes_audio/MiniMax_Vocal_{timestamp}.wav"
    with open(out_path, "wb") as f:
        f.write(wav_data)
    print(f"Salvo em: {out_path}")
