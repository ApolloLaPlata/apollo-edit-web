import os
import modal
import sys

# Adiciona o diretório raiz ao sys.path para importações locais funcionarem
sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

try:
    app = modal.App.lookup("apollo-laplata", create_if_missing=False)
except modal.exception.NotFoundError:
    print("Aviso: app 'apollo-laplata' não encontrada em lookup.")

from backend.cloud_tools.engines.xtts_engine import XttsEngine, app

@app.local_entrypoint()
def main():
    import os
    
    # AQUI ESTÁ O SEGREDO: Usamos a Fase 1 (a mulher rindo) como base para a Fase 2!
    ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\xtts_fase1_mulher_alegria.wav"
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()
        
    print("Iniciando XTTSv2 para a Fase 2 (Sustentação de Emoção)...")
    engine = XttsEngine()
    
    # Um texto mais longo para testar se ela não "perde o fôlego" ou volta a ficar neutra no meio do caminho.
    texto_para_falar = (
        "Gente, vocês não vão acreditar no que acabou de acontecer! Hahaha! "
        "Eu estava testando aquele sistema de clonagem que todo mundo falava, e de repente, bum! "
        "Funcionou perfeitamente logo de cara! Hahaha, é bom demais pra ser verdade, sério. "
        "Eu estou muito feliz com esse resultado, ficou maravilhoso!"
    )
    
    print("Gerando áudio da Matriz XTTS Fase 2...")
    
    # Chama o método remote
    audio_bytes = engine.generate_voice.remote(
        text=texto_para_falar,
        reference_audio_bytes=ref_bytes,
        language="pt",
        temperature=0.75, # Temperatura um pouco alta para permitir mais expressão
        speed=1.0
    )
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "xtts_fase2_mulher_alegria_longo.wav")
    
    with open(save_path, "wb") as f:
        f.write(audio_bytes)
        
    print(f"SUCESSO! Áudio salvo em: {save_path}")
    os.startfile(save_path)
