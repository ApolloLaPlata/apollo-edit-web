import os
import sys
import modal

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

s2_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "build-essential", "portaudio19-dev")
    .pip_install(
        "torch==2.4.0",
        "torchaudio==2.4.0",
        "fastapi[standard]",
        "soundfile",
        "huggingface_hub",
        "httpx"
    )
    .run_commands(
        "git clone https://github.com/fishaudio/fish-speech.git /opt/fish-speech",
        "cd /opt/fish-speech && pip install -e ."
    )
)

fish_volume = modal.Volume.from_name("fish-cache-s2", create_if_missing=True)

app = modal.App("apollo-s2-true", image=s2_image)

@app.cls(
    image=s2_image, 
    gpu="A10G", 
    timeout=900, 
    min_containers=0,
    volumes={"/root/.cache/huggingface": fish_volume}
)
class TrueS2Engine:
    @modal.enter()
    def load_model(self):
        print("[INIT] Carregando S2-Pro na VRAM...")
        from huggingface_hub import snapshot_download
        import subprocess
        import time
        import httpx
        import os
        
        ckpt_dir = snapshot_download(repo_id="fishaudio/s2-pro")
        decoder_pth = os.path.join(ckpt_dir, "codec.pth")
        
        cmd = [
            "python", "tools/api_server.py",
            "--listen", "127.0.0.1:8080",
            "--llama-checkpoint-path", ckpt_dir,
            "--decoder-checkpoint-path", decoder_pth,
            "--decoder-config-name", "modded_dac_vq",
            "--half"
        ]
        
        self.server_proc = subprocess.Popen(cmd, cwd="/opt/fish-speech")
        
        print("[INIT] Aguardando API Server interno do S2 subir...")
        for _ in range(90):
            try:
                r = httpx.get("http://127.0.0.1:8080/v1/health")
                if r.status_code == 200:
                    break
            except Exception:
                pass
            time.sleep(2)
        print("[INIT] S2-Pro Pronto para Geração (Server Online)!")

    @modal.method()
    def generate_voice(self, text: str, reference_audio_bytes: bytes = None, reference_text: str = ""):
        import httpx
        import ormsgpack
        
        payload = {
            "text": text,
            "reference_id": None,
            "references": [],
            "format": "wav",
            "chunk_length": 200,
            "streaming": False
        }
        
        if reference_audio_bytes:
            payload["references"] = [{"audio": reference_audio_bytes, "text": reference_text}]
            
        headers = {"Content-Type": "application/msgpack"}
        packed_data = ormsgpack.packb(payload)
        
        resp = httpx.post("http://127.0.0.1:8080/v1/tts", content=packed_data, headers=headers, timeout=300)
        if resp.status_code != 200:
            raise RuntimeError(f"Fish API Error: {resp.status_code} - {resp.text}")
            
        return resp.content


@app.local_entrypoint()
def main():
    from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT

    ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()

    whisper_engine = WhisperTurboSTT()
    try:
        transcription_result = whisper_engine.transcribe.remote(ref_bytes, language="pt")
        ref_text = transcription_result.get("text", "").strip()
    except Exception as e:
        ref_text = "Texto genérico para ancoragem."

    engine = TrueS2Engine()
    
    testes = [
        ("s2_teste_sussurro", "[whispering] Shhh... Fale baixo, eles estão ouvindo a gente."),
        ("s2_teste_risada_extrema", "[laughing] HAHAHA! Meu Deus, isso é muito engraçado! HAHAHAHA!"),
        ("s2_teste_raiva_extrema", "[angry and shouting] EU JÁ DISSE QUE NÃO! SAI DAQUI AGORA!"),
        ("s2_teste_tristeza", "[crying and sad] Eu não acredito que isso está acontecendo... snif... acabou tudo.")
    ]
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\s2_real"
    os.makedirs(save_dir, exist_ok=True)
    
    for nome, texto in testes:
        print(f"\n-> Processando: {nome}")
        audio_bytes = engine.generate_voice.remote(texto, ref_bytes, ref_text)
        save_path = os.path.join(save_dir, f"{nome}.wav")
        with open(save_path, "wb") as f:
            f.write(audio_bytes)
        print(f"Salvo em: {save_path}")
