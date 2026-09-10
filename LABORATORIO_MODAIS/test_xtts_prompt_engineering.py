import os
import sys

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.engines.xtts_engine import XttsEngine
import modal
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    print("\n--- INICIANDO TESTE: PROMPT ENGINEERING DIRETO NO XTTS (Fase 1) ---")
    engine = XttsEngine()
    
    ref_audio = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    
    with open(ref_audio, "rb") as f:
        audio_data = f.read()
        
    prompts = {
        "raiva_1": "Mas que inferno! Eu não aguento mais isso! Que ódio!!",
        "raiva_2": "Cala a boca! Você não sabe de nada! Eu tô avisando!",
        "alegria_1": "Hahahaha! Nossa, isso é maravilhoso! Que incrível!",
        "alegria_2": "Ahahaha! Ai minha barriga, eu não consigo parar de rir!"
    }
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\xtts_prompts"
    os.makedirs(save_dir, exist_ok=True)
    
    for nome, texto in prompts.items():
        print(f"\n[Gerando XTTS] {nome}: '{texto}'")
        try:
            audio_bytes = engine.generate_voice.remote(
                text=texto,
                language="pt",
                reference_audio_bytes=audio_data
            )
            
            save_path = os.path.join(save_dir, f"{nome}.wav")
            with open(save_path, "wb") as f:
                f.write(audio_bytes)
            print(f"-> Salvo: {save_path}")
        except Exception as e:
            print(f"Erro em {nome}: {e}")
            
    print("\n--- TESTE CONCLUÍDO ---")
