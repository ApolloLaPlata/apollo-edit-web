import os
import sys
import modal

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

try:
    app = modal.App.lookup("apollo-laplata", create_if_missing=False)
except modal.exception.NotFoundError:
    print("Aviso: app 'apollo-laplata' não encontrada em lookup.")

from backend.cloud_tools.engines.fish_engine import FishTTSEngine, app

@app.local_entrypoint()
def main():
    # Áudio original neutro da mulher
    ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    
    if not os.path.exists(ref_audio_path):
        print(f"ERRO: Áudio base não encontrado em {ref_audio_path}")
        return

    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()
        
    print("Iniciando Fish Speech 1.5 (MODAL) para teste de Emoções Extremas...")
    engine = FishTTSEngine()
    
    # O segredo do Fish Speech V1.5 / S2 não é um "botão" ou parâmetro numérico, 
    # mas o treinamento em formatações de Roleplay (Ações entre colchetes)
    emocoes = {
        "fish_modal_raiva": "(furious and screaming with rage) EU NÃO AGUENTO MAIS ISSO!!! (gritando) Isso é um absurdo!",
        "fish_modal_choro": "(crying loudly, sobbing uncontrollably) Eu só queria que fosse diferente... (chorando muito) Por que isso acontece?",
        "fish_modal_risada": "(laughing hysterically) Meu Deus, isso é muito engraçado! (rindo muito) Hahaha!"
    }
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\fish_modal"
    os.makedirs(save_dir, exist_ok=True)
    
    for nome, texto in emocoes.items():
        print(f"\n-> Processando: {nome}")
        print(f"Texto: {texto}")
        
        try:
            audio_bytes = engine.generate_voice.remote(
                text=texto,
                reference_audio_bytes=ref_bytes
            )
            
            save_path = os.path.join(save_dir, f"{nome}.wav")
            with open(save_path, "wb") as f:
                f.write(audio_bytes)
                
            print(f"SUCESSO! Salvo em: {save_path}")
        except Exception as e:
            print(f"ERRO ao gerar {nome}: {e}")

    print("\nProcesso concluído!")
