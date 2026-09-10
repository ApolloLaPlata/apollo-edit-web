import modal
import os

app = modal.App("ace-step-music-engine")

def download_ace_step():
    from huggingface_hub import snapshot_download
    print("Baixando pesos do ACE-Step...")
    snapshot_download("ACE-Step/ACE-Step-v1-3.5B")
    
image = modal.Image.debian_slim().apt_install("git", "ffmpeg").pip_install(
    "torch", "torchaudio", "torchcodec", "transformers", "accelerate", "huggingface_hub", "einops", "soundfile"
).run_commands(
    "git clone https://github.com/ace-step/ACE-Step.git /ACE-Step",
    "pip install -r /ACE-Step/requirements.txt",
    "sed -i 's/target_wav = target_wav.float()/target_wav = target_wav.float()\\n        target_wav = target_wav \\/ (target_wav.abs().max() + 1e-8)\\n        target_wav = target_wav * (10 ** (-1.0 \\/ 20))/g' /ACE-Step/acestep/pipeline_ace_step.py"
).run_function(download_ace_step)

@app.cls(gpu="a10g", image=image, secrets=[modal.Secret.from_name("my-huggingface-secret")], timeout=1200)
class AceStepEngine:
    @modal.enter()
    def setup(self):
        import sys
        sys.path.append("/ACE-Step")
        print("Ambiente ACE-Step carregado com sucesso!")
        
        # O modelo já foi baixado na compilação da imagem
        from huggingface_hub import snapshot_download
        model_path = snapshot_download("ACE-Step/ACE-Step-v1-3.5B")
        
        from acestep.pipeline_ace_step import ACEStepPipeline
        self.model = ACEStepPipeline(
            checkpoint_dir=model_path,
            dtype="bfloat16",
            cpu_offload=False, # Na A10G (24GB), 3.5B cabe na VRAM, sem offload para maior velocidade
            overlapped_decode=False
        )
        print("Modelo carregado na VRAM!")

    @modal.method()
    def generate_song(self, prompt_tags: str, lyrics: str):
        print(f"Gerando música com ACE-Step...")
        print(f"Tags: {prompt_tags}")
        print(f"Lyrics:\n{lyrics}")
        
        save_path = "/tmp/ace_step_output.wav"
        
        self.model(
            audio_duration=30,
            prompt=prompt_tags,
            lyrics=lyrics,
            infer_step=50,
            guidance_scale=4.5,
            scheduler_type="euler",
            cfg_type="true_cfg",
            manual_seeds=42,
            use_erg_tag=False,
            use_erg_lyric=False,
            use_erg_diffusion=False,
            save_path=save_path,
        )
        
        self.model.cleanup_memory()
        
        with open(save_path, "rb") as f:
            return f.read()

@app.local_entrypoint()
def test_ace_step():
    print("Iniciando laboratório de teste ACE-Step (Apache 2.0)...")
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    tags = "funk, pop, soul, rock, melodic, guitar, drums, bass, keyboard, percussion, 105 BPM, energetic, upbeat, groovy, vibrant, dynamic, clear pristine studio recording"
    lyrics = "[Verse]\nI don't care about the view\n'Cause I exist for me and you\nI live my whole life in this planter\nI can't find my car so just call me the\nHorny gardener\n\n[Chorus]\nSticky green time in the flowery bob\nMy top shelf's looking good enough to chew\nRight now every fly in the town is talking to me and buzzing too\nDaisy Daisy can you come outside to play or else\nI'll put a garden stake through you"
    
    engine = AceStepEngine()
    try:
        # Pega a pasta atual onde o app está rodando localmente (onde foi chamado)
        wav_data = engine.generate_song.remote(prompt_tags=tags, lyrics=lyrics)
        out_path = os.path.abspath("LABORATORIO_MODAIS/testes_audio/ace_step_test_funk.wav")
        with open(out_path, "wb") as f:
            f.write(wav_data)
        print(f"Sucesso! Salvo em: {out_path}")
    except Exception as e:
        print(f"Falha na inferência ACE-Step: {e}")
