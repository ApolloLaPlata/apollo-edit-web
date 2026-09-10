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
    
    print("=== TESTE RAFAEL DESCARGAS: XTTS FASE 1 E FASE 2 ===")
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\rafael"
    os.makedirs(save_dir, exist_ok=True)
    
    # 1. Carregar a Referência Base do Rafael (Fala 3 - Limpa e Normalizada)
    ref_neutra_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\fala_3_rafael_clean.wav"
    with open(ref_neutra_path, "rb") as f:
        ref_rafael_bytes = f.read()

    # Bateria de Textos (Fase 1 vs Fase 2)
    testes = [
        ("01_angry", 
         "EU NÃO AGUENTO MAIS ISSO!!! Você prometeu que ia mudar... e mais uma vez eu tô aqui, repetindo a mesma conversa.",
         "Eu já falei mil vezes que o prazo era ontem! Como vocês têm a audácia de me entregar isso agora?!"),
        ("02_crying", 
         "Eu... eu juro que tentei... mas nada do que eu faço é o suficiente... por favor... só me diz que vai ficar tudo bem...",
         "Por favor... me diz que isso é mentira... eu não consigo acreditar que ele se foi pra sempre..."),
        ("03_laughing", 
         "HAHAHA... eu não acredito que você fez ISSO mesmo! cara, sério... eu tô chorando de rir aqui... só... só me dá um segundo... HAHAHA...",
         "Mano, você tinha que ver a cara dele quando a porta abriu! HAHAHA! Foi a coisa mais bizarra do mundo, sério!"),
        ("04_mixed", 
         "Eu fiz TUDO que você pediu... e ainda assim não foi suficiente pra você, né? fala logo a verdade... o que mais você quer que eu faça?!",
         "Eu não tô acreditando que você escondeu isso de mim... depois de tudo que a gente passou! Sai daqui agora, eu não quero olhar na sua cara!")
    ]
    
    engine = XttsEngine()
    
    for nome, txt_fase1, txt_fase2 in testes:
        print(f"\n--- Processando Rafael (Fala 3): {nome} ---")
        
        # PASSO 1: FASE 1 (Criar Âncora Emocional do Rafael)
        print(" -> [1] Gerando Fase 1 (Âncora Emocional)...")
        xtts_fase1_bytes = engine.generate_voice.remote(
            text=txt_fase1,
            reference_audio_bytes=ref_rafael_bytes,
            language="pt",
            temperature=0.65,
            speed=1.0
        )
        fase1_path = os.path.join(save_dir, f"1_rafael_fase1_{nome}.wav")
        with open(fase1_path, "wb") as f:
            f.write(xtts_fase1_bytes)
            
        # PASSO 2: FASE 2 (Transferência de Emoção usando o Fase 1 como referência)
        print(" -> [2] Gerando Fase 2 (Novo texto com a âncora gerada)...")
        xtts_fase2_bytes = engine.generate_voice.remote(
            text=txt_fase2,
            reference_audio_bytes=xtts_fase1_bytes,
            language="pt",
            temperature=0.65,
            speed=1.0
        )
        fase2_path = os.path.join(save_dir, f"2_rafael_fase2_{nome}.wav")
        with open(fase2_path, "wb") as f:
            f.write(xtts_fase2_bytes)
            
    print("\n=== TESTE DO RAFAEL CONCLUÍDO ===")
    print(f"Arquivos salvos em: {save_dir}")
