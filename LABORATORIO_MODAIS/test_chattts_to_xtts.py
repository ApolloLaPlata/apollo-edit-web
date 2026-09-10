import os
import sys

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.engines.chat_tts_engine import ChatTTSEngine
from backend.cloud_tools.engines.xtts_engine import XttsEngine
import modal

# Pegando os apps
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    print("\n--- INICIANDO TESTE: ChatTTS (Inglês) -> XTTS (Português) ---")
    
    # 1. Gerar a Âncora Emocional no ChatTTS (Inglês)
    chat_engine = ChatTTSEngine()
    
    texto_eng = "Oh my god! [laugh] This is so funny! Hahahaha! I can't stop laughing! [laugh]"
    print(f"\n[Fase 1 - ChatTTS] Gerando âncora em Inglês: '{texto_eng}'")
    
    anchor_bytes = chat_engine.generate_audio.remote(
        text=texto_eng,
        temperature=0.7, 
        refine_prompt='[oral_2][laugh_0][break_4]'
    )
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais"
    os.makedirs(save_dir, exist_ok=True)
    
    anchor_path = os.path.join(save_dir, "chattts_anchor_laugh_en.wav")
    with open(anchor_path, "wb") as f:
        f.write(anchor_bytes)
        
    print(f"-> Âncora ChatTTS salva em: {anchor_path}")
    
    # 2. Injetar a Âncora no XTTS e gerar em Português
    xtts_engine = XttsEngine()
    
    texto_pt = "Nossa, que maravilha! Eu não acredito que isso funcionou tão bem! Hahahaha!"
    print(f"\n[Fase 2 - XTTS] Gerando clonagem cruzada em Português: '{texto_pt}'")
    
    with open(anchor_path, "rb") as f:
        audio_data = f.read()
        
    final_bytes = xtts_engine.generate_audio.remote(
        text=texto_pt,
        language="pt",
        speaker_audio_data=audio_data,
        speaker_filename="chattts_anchor_laugh_en.wav"
    )
    
    final_path = os.path.join(save_dir, "xtts_final_from_chattts_pt.wav")
    with open(final_path, "wb") as f:
        f.write(final_bytes)
        
    print(f"-> Resultado XTTS salvo em: {final_path}")
    print("\n--- TESTE CONCLUÍDO ---")
    
    # Tocar os dois para comparação (opcional)
    # os.startfile(anchor_path)
    # import time; time.sleep(3)
    # os.startfile(final_path)

