import modal
import base64
import os
import time

app = modal.App("test-cloud-engines")

@app.local_entrypoint()
def test_all():
    os.makedirs("testes_finais_api", exist_ok=True)
    
    print("\n--- TESTANDO ACE-STEP 1.5 ---")
    from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine
    try:
        engine_ace = AceStep15Engine()
        fc = engine_ace.generate.remote(style_tags="trap vocal", lyrics="[Verse] TESTE", length_seconds=10, steps=64)
        if fc.get("status") == "success":
            print(f"ACE-STEP OK! (Tempo: {fc.get('render_time_seconds')}s)")
        else:
            print("ACE-STEP FALHOU:", fc)
    except Exception as e:
        print("ACE-STEP EXCEPTION:", e)
        
    print("\n--- TESTANDO SA3 ---")
    from backend.cloud_tools.engines.stable_audio_engine import StableAudioEngine
    try:
        engine_sa3 = StableAudioEngine()
        b64 = engine_sa3.generate_audio.remote(prompt="drum beat", duration_s=10.0, num_inference_steps=10) # uso 10 steps apenas para o teste ser rapido
        if b64:
            print("SA3 OK! (Tamanho B64: {})".format(len(b64)))
        else:
            print("SA3 FALHOU (Retornou vazio)")
    except Exception as e:
        print("SA3 EXCEPTION:", e)

    print("\n--- TESTANDO MINIMAX ---")
    from backend.cloud_tools.engines.minimax_engine import MinimaxEngine
    try:
        engine_mini = MinimaxEngine()
        b64 = engine_mini.generate.remote(prompt="drum loop", is_instrumental=True, lyrics="", duration=10.0)
        if b64:
            print("MINIMAX OK! (Tamanho B64: {})".format(len(b64)))
        else:
            print("MINIMAX FALHOU (Retornou vazio)")
    except Exception as e:
        print("MINIMAX EXCEPTION:", e)

print("Teste iniciado...")
