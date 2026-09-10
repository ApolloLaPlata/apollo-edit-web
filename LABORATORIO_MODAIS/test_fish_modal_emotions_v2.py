import os
import sys
import modal

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

try:
    app = modal.App.lookup("apollo-laplata", create_if_missing=False)
except modal.exception.NotFoundError:
    print("Aviso: app 'apollo-laplata' não encontrada em lookup.")

from backend.cloud_tools.engines.fish_engine import FishTTSEngine, app
from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT

@app.local_entrypoint()
def main():
    ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    
    if not os.path.exists(ref_audio_path):
        print(f"ERRO: Áudio base não encontrado em {ref_audio_path}")
        return

    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()
        
    print("Transcrevendo o áudio de referência para ancoragem perfeita no Fish Speech...")
    whisper_engine = WhisperTurboSTT()
    
    try:
        # Pega o texto real do áudio para não quebrar a decodificação semântica
        transcription_result = whisper_engine.transcribe.remote(ref_bytes, language="pt")
        ref_text = transcription_result.get("text", "").strip()
        print(f"Texto transcrito: {ref_text}")
    except Exception as e:
        print(f"Erro ao transcrever, usando texto genérico: {e}")
        ref_text = "Texto genérico para ancoragem."

    print("Iniciando Fish Speech 1.5 (MODAL) com a Transcrição Injetada...")
    engine = FishTTSEngine()
    
    # As pesquisas apontam que para Forçar o Prompt Engineering Emocional no Fish, 
    # Precisamos do texto âncora exato (acima) + o uso das tags certas.
    emocoes = {
        "fish_modal_raiva": "[furious and shouting loudly] EU NÃO AGUENTO MAIS ISSO!!!",
        "fish_modal_choro": "[crying loudly][sobbing uncontrollably] Eu só queria que fosse diferente...",
        "fish_modal_risada": "[laughing hysterically] Meu Deus, isso é muito engraçado!"
    }
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\fish_modal"
    os.makedirs(save_dir, exist_ok=True)
    
    for nome, texto in emocoes.items():
        print(f"\n-> Processando: {nome}")
        
        try:
            audio_bytes = engine.generate_voice.remote(
                text=texto,
                reference_audio_bytes=ref_bytes,
                reference_text=ref_text
            )
            
            save_path = os.path.join(save_dir, f"{nome}.wav")
            with open(save_path, "wb") as f:
                f.write(audio_bytes)
                
            print(f"SUCESSO! Salvo em: {save_path}")
        except Exception as e:
            print(f"ERRO ao gerar {nome}: {e}")

    print("\nProcesso concluído!")
