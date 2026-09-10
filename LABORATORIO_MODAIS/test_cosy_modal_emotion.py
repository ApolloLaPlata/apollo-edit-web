import os
import sys

# Ajustar o sys.path para encontrar a pasta backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.cloud_tools.engines.cosyvoice_engine import CosyVoiceEngine, app
import modal

@app.local_entrypoint()
def main():
    print("Iniciando motor CosyVoice2...")
    engine = CosyVoiceEngine()
    
    texto_da_referencia = "Este é um teste de voz em português brasileiro para analisarmos a fluidez, sotaque e velocidade de geração do modelo.com."
    ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    
    with open(ref_audio_path, "rb") as f:
        ref_audio_bytes = f.read()
    
    prompts = {
        "cosyvoice_laugh_forced": {
            "text": "Oh my god, this is hilarious! I can't stop laughing! [laughs]",
            "instruct": "Laughing out loud, very happy and hysterical."
        },
        "cosyvoice_cry_forced": {
            "text": "Please... no... I don't want this to happen. [sighs] It hurts so much.",
            "instruct": "Crying, very sad, sobbing and desperate."
        }
    }
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\cosyvoice"
    os.makedirs(save_dir, exist_ok=True)

    for name, data in prompts.items():
        print(f"\n[CosyVoice] Generating: {name}")
        audio_bytes = engine.generate_voice.remote(
            tts_text=data["text"],
            instruct_text=data["instruct"],
            prompt_text=texto_da_referencia,
            reference_audio_bytes=ref_audio_bytes
        )
        save_path = os.path.join(save_dir, f"{name}.wav")
        with open(save_path, "wb") as f:
            f.write(audio_bytes)
        print(f"SUCESSO! Áudio salvo em: {save_path}")
    os.startfile(save_path)
