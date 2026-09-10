import os
import modal

app = modal.App("apollo-fish-s2")

# Imagem Modal com todas as dependências do S2-Pro (Transformers)
s2_image = (
    modal.Image.from_registry("nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04", add_python="3.11")
    .apt_install("ffmpeg", "libsndfile1", "git")
    .pip_install(
        "torch>=2.1.0",
        "git+https://github.com/huggingface/transformers.git",
        "accelerate",
        "librosa",
        "soundfile",
        "numpy<2.0",
        "huggingface_hub"
    )
)

MODEL_ID = "fishaudio/s2-pro"

@app.cls(
    image=s2_image,
    gpu="L4", # GPU poderosa para inferência e cache
    timeout=600,
    enable_memory_snapshot=True,
)
class FishS2Engine:
    @modal.enter()
    def load_model(self):
        import torch
        from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
        
        print(f"Loading Fish Speech S2 ({MODEL_ID}) into VRAM...")
        self.device = "cuda"
        
        # Download and load processor
        self.processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
        
        # Download and load model in FP16 to save memory and speed up
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MODEL_ID, 
            torch_dtype=torch.float16, 
            device_map="auto",
            trust_remote_code=True
        )
        print("S2 Model loaded successfully!")

    @modal.method()
    def synthesize_emotion(self, text: str, ref_audio_bytes: bytes):
        import torch
        import soundfile as sf
        import librosa
        import io
        
        print(f"[GEN] S2-Pro Processing Text: {text}")
        
        # Decode reference audio using librosa via an in-memory file
        with open("/tmp/ref_audio.wav", "wb") as f:
            f.write(ref_audio_bytes)
            
        ref_audio, sr = librosa.load("/tmp/ref_audio.wav", sr=self.processor.feature_extractor.sampling_rate)
        
        # Process inputs
        inputs = self.processor(
            text=text, 
            audios=ref_audio, 
            sampling_rate=sr, 
            return_tensors="pt"
        ).to(self.device, torch.float16)

        # Generate audio
        with torch.no_grad():
            out = self.model.generate(
                **inputs, 
                temperature=0.8, 
                top_p=0.85, 
                top_k=50
            )
            
        # Decode output
        audio = self.processor.batch_decode(out, skip_special_tokens=True, output_type="np")[0]
        
        # Save to memory buffer
        out_buffer = io.BytesIO()
        sf.write(out_buffer, audio, sr, format="WAV")
        return out_buffer.getvalue()

@app.local_entrypoint()
def main():
    ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    
    if not os.path.exists(ref_audio_path):
        print(f"ERRO: Áudio base não encontrado em {ref_audio_path}")
        return

    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()

    print("Iniciando Fish Speech S2-Pro (Modal)... (O primeiro run pode demorar baixando os pesos)")
    engine = FishS2Engine()
    
    # As tags [] agora são comandos internos!
    emocoes = {
        "fish_s2_raiva": "[furious and shouting loudly] EU NÃO AGUENTO MAIS ISSO!!!",
        "fish_s2_choro": "[crying loudly][sobbing uncontrollably] Eu só queria que fosse diferente...",
        "fish_s2_risada": "[laughing hysterically] Meu Deus, isso é muito engraçado!"
    }
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\fish_s2_pro"
    os.makedirs(save_dir, exist_ok=True)
    
    for nome, texto in emocoes.items():
        print(f"\n-> S2 Gerando: {nome}")
        
        try:
            audio_bytes = engine.synthesize_emotion.remote(text=texto, ref_audio_bytes=ref_bytes)
            
            save_path = os.path.join(save_dir, f"{nome}.wav")
            with open(save_path, "wb") as f:
                f.write(audio_bytes)
                
            print(f"SUCESSO! Salvo em: {save_path}")
        except Exception as e:
            print(f"ERRO ao gerar {nome}: {e}")

    print("\nTeste S2 Concluído!")
