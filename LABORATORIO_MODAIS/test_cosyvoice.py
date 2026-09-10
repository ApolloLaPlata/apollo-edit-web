import os
import sys
import modal

cosy_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libsndfile1")
    .run_commands("git clone https://github.com/FunAudioLLM/CosyVoice.git /cosyvoice")
    .run_commands("cd /cosyvoice && git submodule update --init --recursive")
    .run_commands("cd /cosyvoice && sed -i 's/openai-whisper==20231117/openai-whisper/g' requirements.txt")
    .run_commands("cd /cosyvoice && pip install -r requirements.txt")
    .run_commands("cd /cosyvoice && pip install -r requirements.txt")
    .pip_install("modelscope", "torchaudio", "pydub", "torch")
)

app = modal.App("apollo-cosyvoice-test")

@app.function(image=cosy_image, gpu="L4", timeout=600)
def generate_cosyvoice(text: str, ref_wav_bytes: bytes, ref_text: str):
    import sys
    sys.path.append('/cosyvoice')
    from cosyvoice.cli.cosyvoice import CosyVoice
    from modelscope import snapshot_download
    import torchaudio
    import io
    
    print("Downloading CosyVoice-300M model...")
    model_dir = snapshot_download('iic/CosyVoice-300M')
    print("Initializing CosyVoice...")
    cosyvoice = CosyVoice(model_dir)
    
    with open("/tmp/ref.wav", "wb") as f:
        f.write(ref_wav_bytes)
        
    prompt_speech_16k = torchaudio.load("/tmp/ref.wav")[0]
    
    print(f"Generating audio for text: {text}")
    output = cosyvoice.inference_zero_shot(
        tts_text=text,
        prompt_text=ref_text,
        prompt_speech=prompt_speech_16k
    )
    
    for j in output:
        out_io = io.BytesIO()
        torchaudio.save(out_io, j['tts_speech'], 22050, format="wav")
        return out_io.getvalue()

@app.local_entrypoint()
def main():
    print("\n--- INICIANDO TESTE: COSYVOICE (Zero-Shot Clone) ---")
    
    ref_audio = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    with open(ref_audio, "rb") as f:
        audio_data = f.read()
        
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\cosyvoice"
    os.makedirs(save_dir, exist_ok=True)
    
    ref_text = "Este é um teste de voz em português brasileiro para analisarmos a fluidez, sotaque e velocidade de geração do modelo.com."
    
    prompts = {
        "laugh_forced": "[laugh] Oh my god, this is hilarious! I can't stop laughing! [laugh]",
        "cry_forced": "Please... no... I don't want this to happen. [cry] It hurts so much."
    }
    
    for name, text in prompts.items():
        print(f"\n[CosyVoice] Generating: {name} -> {text}")
        try:
            wav_bytes = generate_cosyvoice.remote(text, audio_data, ref_text)
            save_path = os.path.join(save_dir, f"{name}.wav")
            with open(save_path, "wb") as f:
                f.write(wav_bytes)
            print(f"-> Salvo: {save_path}")
        except Exception as e:
            print(f"Erro em {name}: {e}")
            
    print("\n--- TESTE COSYVOICE CONCLUÍDO ---")
