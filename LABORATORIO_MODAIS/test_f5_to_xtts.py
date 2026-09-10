import os
import sys

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.engines.f5_engine import F5TTSEngine
from backend.cloud_tools.engines.xtts_engine import XttsEngine
import modal
import subprocess
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    print("\n--- INICIANDO TESTE: F5-TTS (Âncora Inglesa) -> XTTS (Português) ---")
    
    # Áudio original da mulher
    ref_audio = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    with open(ref_audio, "rb") as f:
        audio_data = f.read()
        
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\f5_xtts_cross"
    os.makedirs(save_dir, exist_ok=True)
    
    # --- FASE 1: F5-TTS ---
    print("\n[Fase 1] Gerando âncora emocional hiper-realista em Inglês (F5-TTS)...")
    f5_engine = F5TTSEngine()
    
    texto_eng = "Oh my god! Hahahaha! I can't believe this! It's so funny! Hahahaha!"
    
    wav_bytes = f5_engine.generate_voice.remote(
        text=texto_eng,
        reference_audio_bytes=audio_data,
        ref_text=""
    )
    
    anchor_wav_path = os.path.join(save_dir, "f5_anchor_en.wav")
    with open(anchor_wav_path, "wb") as f:
        f.write(wav_bytes)
        
    print(f"-> Âncora F5-TTS salva: {anchor_wav_path}")
    
    # --- FASE 2: XTTS ---
    print("\n[Fase 2] Clonando a âncora inglesa para o Português (XTTS)...")
    xtts_engine = XttsEngine()
    
    with open(anchor_wav_path, "rb") as f:
        f5_wav_data = f.read()
        
    texto_pt = "Nossa, que maravilha! Eu não acredito que isso funcionou tão bem! Hahahaha!"
    
    xtts_bytes = xtts_engine.generate_voice.remote(
        text=texto_pt,
        language="pt",
        reference_audio_bytes=f5_wav_data
    )
    
    final_path = os.path.join(save_dir, "xtts_final_pt.wav")
    with open(final_path, "wb") as f:
        f.write(xtts_bytes)
        
    print(f"-> Resultado final XTTS salvo: {final_path}")
    print("\n--- TESTE CONCLUÍDO ---")
