import modal
import os
apollo_volume = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)

app = modal.App("yue-music-engine")

image = modal.Image.from_registry(
    "nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.11"
).apt_install("git", "ffmpeg", "git-lfs", "build-essential", "clang").run_commands(
    "git lfs install",
    "pip install wheel setuptools ninja packaging",
    "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
).pip_install(
    "transformers<4.50.0", "accelerate", "huggingface_hub", "einops", "soundfile", 
    "omegaconf", "sentencepiece", "tqdm", "tensorboard", "descript-audiotools>=0.7.2", "descript-audio-codec", "scipy"
).run_commands(
    "pip install flash-attn --no-build-isolation",
    "git clone https://github.com/multimodal-art-projection/YuE.git /YuE"
)

@app.cls(gpu="H100", image=image, volumes={"/apollo_volume": apollo_volume}, timeout=1200)
class YuEEngine:
    @modal.enter()
    def setup(self):
        import sys
        import shutil
        sys.path.append("/YuE")
        os.system("sed -i 's/# device_map=\"auto\",/device_map=\"cuda:0\",/g' /YuE/inference/infer.py")
        os.system("sed -i 's/len(lyrics))/len(lyrics)+1)/g' /YuE/inference/infer.py")
        print("Copiando tokenizadores e codecs do Volume para a pasta do YuE...")
        
        # O infer.py do YuE espera encontrar as pastas de codecs nativamente em sua pasta de inferência
        os.makedirs("/YuE/inference/xcodec_mini_infer", exist_ok=True)
        os.makedirs("/YuE/inference/mm_tokenizer_v0.2_hf", exist_ok=True)
        
        if os.path.exists("/apollo_volume/models/yue/xcodec_mini_infer"):
            os.system("cp -r /apollo_volume/models/yue/xcodec_mini_infer/* /YuE/inference/xcodec_mini_infer/")
        if os.path.exists("/apollo_volume/models/yue/mm_tokenizer_v0.2_hf"):
            os.system("cp -r /apollo_volume/models/yue/mm_tokenizer_v0.2_hf/* /YuE/inference/mm_tokenizer_v0.2_hf/")
            
        print("Ambiente YuE carregado com sucesso a partir do apollo_volume!")
        
    @modal.method()
    def generate_song(self, prompt_tags: str, lyrics: str):
        print(f"Gerando música com YuE (Lyrics2Song)...")
        import tempfile
        import subprocess
        import os
        import glob
        
        with tempfile.TemporaryDirectory() as tmpdir:
            genre_path = os.path.join(tmpdir, "genre.txt")
            lyrics_path = os.path.join(tmpdir, "lyrics.txt")
            out_dir = os.path.join(tmpdir, "output")
            os.makedirs(out_dir, exist_ok=True)
            
            with open(genre_path, "w", encoding="utf-8") as f:
                f.write(prompt_tags)
                
            with open(lyrics_path, "w", encoding="utf-8") as f:
                # O YuE espera seções no formato [verse], [chorus]. Se não tiver, adicionamos algo básico.
                if "[" not in lyrics:
                    lyrics = f"[verse]\n{lyrics}"
                f.write(lyrics)
                
            cmd = [
                "python", "/YuE/inference/infer.py",
                "--cuda_idx", "0",
                "--stage1_model", "/apollo_volume/models/yue/YuE-s1-7B-anneal-en-cot",
                "--stage2_model", "/apollo_volume/models/yue/YuE-s2-1B-general",
                "--genre_txt", genre_path,
                "--lyrics_txt", lyrics_path,
                "--run_n_segments", "2", 
                "--stage2_batch_size", "4",
                "--output_dir", out_dir,
                "--max_new_tokens", "6000",
                "--repetition_penalty", "1.1"
            ]
            print(f"Executando YuE subprocess: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="/YuE/inference")
            print("YuE STDOUT:", result.stdout)
            
            if result.returncode != 0:
                print("YuE STDERR:", result.stderr)
                raise RuntimeError("Falha na geração do YuE")
                
            # Procurar arquivos MP3 ou WAV gerados
            audio_files = glob.glob(os.path.join(out_dir, "**", "*.mp3"), recursive=True)
            if not audio_files:
                audio_files = glob.glob(os.path.join(out_dir, "**", "*.wav"), recursive=True)
                
            if not audio_files:
                raise FileNotFoundError(f"Áudio não encontrado no diretório de saída: {out_dir}")
                
            mix_file = None
            for af in audio_files:
                if "mixed.mp3" in af.lower():
                    mix_file = af
                    break
            if not mix_file:
                mix_file = audio_files[0]
                    
            import tempfile
            mix_file_norm = mix_file.replace(".mp3", "_norm.mp3")
            print("Aplicando masterizacao no YuE...")
            subprocess.run([
                "ffmpeg", "-y", "-i", mix_file,
                "-af", "loudnorm=I=-14:LRA=11:TP=-1.0",
                mix_file_norm
            ], capture_output=True)
            
            with open(mix_file_norm, "rb") as f:
                return f.read()

@app.local_entrypoint()
def test_yue():
    print("Iniciando laboratório de teste YuE (Apache 2.0)...")
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    tags = "vocal-heavy, lead female singer, synth-pop, energetic, 120 bpm"
    lyrics = "[Verse]\nBRILHANDO NAS LUZES DA CIDADE\nNOS ESTAMOS VIVOS\n(Voz ecoando)\n[Chorus]\nE A NOITE NAO TEM FIM\n[Verse]\nTODO O MUNDO SENTE A ENERGIA\nSUANDO ATE O AMANHECER"
    
    engine = YuEEngine()
    try:
        wav_data = engine.generate_song.remote(prompt_tags=tags, lyrics=lyrics)
        out_path = "LABORATORIO_MODAIS/testes_audio/yue_test.wav"
        with open(out_path, "wb") as f:
            f.write(wav_data)
        print(f"Sucesso! Salvo em: {out_path}")
    except Exception as e:
        print(f"Falha na inferência YuE: {e}")
