import os
import sys
import modal

sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

try:
    app = modal.App.lookup("apollo-laplata", create_if_missing=False)
except modal.exception.NotFoundError:
    print("Aviso: app 'apollo-laplata' não encontrada em lookup.")

from backend.cloud_tools.engines.xtts_engine import XttsEngine, app

@app.local_entrypoint()
def main():
    import os
    
    print("=== TESTE DE TRANSFERÊNCIA DE EMOÇÃO: XTTS FASE 2 COM NOVO TEXTO ===")
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\transferencia"
    os.makedirs(save_dir, exist_ok=True)
    
    # As âncoras geradas pelo XTTS Puro no teste anterior
    base_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\shootout"
    
    testes = [
        ("01_angry", "Eu já falei mil vezes que o prazo era ontem! Como vocês têm a audácia de me entregar isso agora?!"),
        ("02_crying", "Por favor... me diz que isso é mentira... eu não consigo acreditar que ele se foi pra sempre..."),
        ("03_laughing", "Mano, você tinha que ver a cara dele quando a porta abriu! HAHAHA! Foi a coisa mais bizarra do mundo, sério!"),
        ("04_mixed", "Eu não tô acreditando que você escondeu isso de mim... depois de tudo que a gente passou! Sai daqui agora, eu não quero olhar na sua cara!")
    ]
    
    engine = XttsEngine()
    
    for nome, novo_texto in testes:
        print(f"\n--- Processando Transferência: {nome} ---")
        
        ref_path = os.path.join(base_dir, f"1_xtts_puro_{nome}.wav")
        if not os.path.exists(ref_path):
            print(f" !!! Referência não encontrada: {ref_path}")
            continue
            
        with open(ref_path, "rb") as f:
            ref_bytes = f.read()
            
        print(f" -> Gerando novo texto usando a âncora {nome}...")
        audio_bytes = engine.generate_voice.remote(
            text=novo_texto,
            reference_audio_bytes=ref_bytes,
            language="pt",
            temperature=0.75,
            speed=1.0
        )
        
        save_path = os.path.join(save_dir, f"xtts_transfer_{nome}.wav")
        with open(save_path, "wb") as f:
            f.write(audio_bytes)
            
        print(f" -> Salvo em: {save_path}")
            
    print("\n=== TRANSFERÊNCIA CONCLUÍDA ===")
    print(f"Arquivos salvos em: {save_dir}")
