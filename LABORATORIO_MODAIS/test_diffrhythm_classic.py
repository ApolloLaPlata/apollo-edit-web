import modal
import os
import time

app = modal.App("diffrhythm-engine-classic")

image = modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10") \
    .apt_install("git", "ffmpeg", "espeak-ng") \
    .pip_install("torch", "torchaudio", "torchvision", extra_options="--index-url https://download.pytorch.org/whl/cu121") \
    .run_commands("git clone https://github.com/ASLP-lab/DiffRhythm.git /DiffRhythm") \
    .run_commands("pip install -r /DiffRhythm/requirements.txt")

@app.cls(gpu="A10G", image=image, timeout=1200)
class DiffRhythmEngine:
    @modal.method()
    def generate(self, prompt: str, duration: str = "120"):
        import subprocess
        import glob
        import tempfile
        import time
        import os
        print(f"Gerando instrumental via subprocess (DiffRhythm): {prompt}")
        
        start = time.time()
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = [
                "python", "infer/infer.py",
                "--ref-prompt", prompt,
                "--audio-length", duration,
                "--chunked",
                "--output-dir", tmpdir
            ]
            print("Executando:", " ".join(cmd))
            res = subprocess.run(cmd, cwd="/DiffRhythm", capture_output=True, text=True)
            print("STDOUT:", res.stdout)
            if res.returncode != 0:
                print("STDERR:", res.stderr)
                raise Exception("Falha na geraçao DiffRhythm")
                
            out_files = glob.glob(os.path.join(tmpdir, "*.wav"))
            if not out_files:
                raise FileNotFoundError("Arquivo de saída não encontrado")
                
            with open(out_files[0], "rb") as f:
                data = f.read()
            print(f"Gerado em {time.time()-start:.1f} segundos!")
            return data

@app.local_entrypoint()
def run_test():
    os.makedirs("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/testes_audio", exist_ok=True)
    engine = DiffRhythmEngine()
    prompt = "Beautiful classical acoustic guitar solo, calm, peaceful, emotional melody, rich strings, fingerstyle, purely instrumental, 44100hz"
    print("Iniciando requisição para DiffRhythm na nuvem (A10G) - Violão Clássico...")
    wav_data = engine.generate.remote(prompt, duration="120")
    
    timestamp = int(time.time())
    out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/testes_audio/DiffRhythm_Violao_{timestamp}.wav"
    with open(out_path, "wb") as f:
        f.write(wav_data)
    print(f"Salvo em: {out_path}")
