import modal
import os

app = modal.App("test-shootout-musical")

@app.local_entrypoint()
def test_all():
    print("Iniciando bateria de testes musicais: STABLE AUDIO OPEN (Alta Fidelidade 44.1kHz)")
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    try:
        StableAudioEngine = modal.Cls.from_name("apollo-cloud-tools", "StableAudioEngine")
        engine_sa = StableAudioEngine()
        print("Gerando música com Stable Audio Open (10s)...")
        audio_bytes = engine_sa.generate_audio.remote(
            prompt="Cinematic epic orchestral trailer music with heavy drums and brass, 44100hz, high fidelity, 120 bpm",
            duration_s=10.0,
            num_inference_steps=100
        )
        with open("LABORATORIO_MODAIS/testes_audio/1_stable_audio_test.wav", "wb") as f:
            f.write(audio_bytes)
        print("✅ Stable Audio salvo em: LABORATORIO_MODAIS/testes_audio/1_stable_audio_test.wav")
    except Exception as e:
        print(f"❌ Erro ao testar Stable Audio: {e}")
