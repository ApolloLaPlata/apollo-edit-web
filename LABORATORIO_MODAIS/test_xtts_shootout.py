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
    
    print("=== INICIANDO O SHOOTOUT SUPREMO: XTTS vs FISH-SPEECH ===")
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\shootout"
    os.makedirs(save_dir, exist_ok=True)
    
    # 1. Carregar a Referência Base Neutra
    ref_neutra_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    with open(ref_neutra_path, "rb") as f:
        ref_neutra_bytes = f.read()

    # Textos do Shootout (Sem as tags de bracket, porque o XTTS tenta ler elas)
    testes = [
        ("01_angry", "EU NÃO AGUENTO MAIS ISSO!!! Você prometeu que ia mudar... e mais uma vez eu tô aqui, repetindo a mesma conversa."),
        ("02_crying", "Eu... eu juro que tentei... mas nada do que eu faço é o suficiente... por favor... só me diz que vai ficar tudo bem..."),
        ("03_laughing", "HAHAHA... eu não acredito que você fez ISSO mesmo! cara, sério... eu tô chorando de rir aqui... só... só me dá um segundo... HAHAHA..."),
        ("04_mixed", "Eu fiz TUDO que você pediu... e ainda assim não foi suficiente pra você, né? fala logo a verdade... o que mais você quer que eu faça?!")
    ]
    
    engine = XttsEngine()
    
    for nome, texto in testes:
        print(f"\n--- Processando Bateria: {nome} ---")
        
        # PASSO 1: XTTS PURO (Fase 1)
        print(" -> [1] Gerando XTTS Puro (Fase 1)...")
        xtts_puro_bytes = engine.generate_voice.remote(
            text=texto,
            reference_audio_bytes=ref_neutra_bytes,
            language="pt",
            temperature=0.75,
            speed=1.0
        )
        puro_path = os.path.join(save_dir, f"1_xtts_puro_{nome}.wav")
        with open(puro_path, "wb") as f:
            f.write(xtts_puro_bytes)
            
        # PASSO 2: XTTS Fase 2 (Ref = XTTS Puro)
        print(" -> [2] Gerando XTTS Fase 2 (Ref = XTTS Puro)...")
        xtts_fase2_xtts_bytes = engine.generate_voice.remote(
            text=texto,
            reference_audio_bytes=xtts_puro_bytes,
            language="pt",
            temperature=0.75,
            speed=1.0
        )
        fase2_xtts_path = os.path.join(save_dir, f"2_xtts_fase2_xtts_{nome}.wav")
        with open(fase2_xtts_path, "wb") as f:
            f.write(xtts_fase2_xtts_bytes)

        # PASSO 3: XTTS Fase 2 (Ref = Fish S2 Extremo)
        print(" -> [3] Gerando XTTS Fase 2 (Ref = Fish S2 Extremo)...")
        s2_ref_path = rf"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\s2_real\matrix_extrema\extreme_{nome}.wav"
        
        if os.path.exists(s2_ref_path):
            with open(s2_ref_path, "rb") as f:
                s2_ref_bytes = f.read()
                
            xtts_fase2_s2_bytes = engine.generate_voice.remote(
                text=texto,
                reference_audio_bytes=s2_ref_bytes,
                language="pt",
                temperature=0.75,
                speed=1.0
            )
            fase2_s2_path = os.path.join(save_dir, f"3_xtts_fase2_s2_{nome}.wav")
            with open(fase2_s2_path, "wb") as f:
                f.write(xtts_fase2_s2_bytes)
        else:
            print(f" !!! Referência S2 não encontrada: {s2_ref_path}")
            
    print("\n=== SHOOTOUT CONCLUÍDO ===")
    print(f"Arquivos salvos em: {save_dir}")
