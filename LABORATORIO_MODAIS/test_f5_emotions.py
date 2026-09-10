import os
import sys

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.engines.f5_engine import F5TTSEngine
import modal
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    print("\n--- INICIANDO TESTE: LAPIDAÇÃO DE ÂNCORAS F5-TTS (WAV PURO) ---")
    
    ref_audio = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    with open(ref_audio, "rb") as f:
        audio_data = f.read()
        
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\f5_anchors"
    os.makedirs(save_dir, exist_ok=True)
    
    f5_engine = F5TTSEngine()
    
    # 5 testes extremos para ver a flexibilidade emocional do modelo em inglês
    prompts = {
        "anger": "Are you serious right now?! I cannot believe you did this! This is completely unacceptable! Get out!",
        "joy": "Hahahaha! Oh my god, this is the best thing ever! I am so happy right now! Hahahaha!",
        "sadness": "I... I just don't understand... Why did this happen? It hurts so much to think about it...",
        "fear": "Wait... what was that noise? Oh my god, is someone there?! Please, help me!",
        "whisper": "Hey... keep your voice down. You need to be very quiet, okay? We can't let them hear us..."
    }
    
    for nome, texto in prompts.items():
        print(f"\n[Gerando F5] {nome}: '{texto}'")
        try:
            # Retorna o WAV puro
            wav_bytes = f5_engine.generate_voice.remote(
                text=texto,
                reference_audio_bytes=audio_data,
                ref_text=""
            )
            
            save_path = os.path.join(save_dir, f"{nome}.wav")
            with open(save_path, "wb") as f:
                f.write(wav_bytes)
            print(f"-> Salvo: {save_path}")
        except Exception as e:
            print(f"Erro em {nome}: {e}")
            
    print("\n--- TESTE DE ÂNCORAS CONCLUÍDO ---")
