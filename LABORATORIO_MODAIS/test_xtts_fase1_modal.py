import os
import modal

# Conectando à app Modal existente do Apollo
try:
    app = modal.App.lookup("apollo-laplata", create_if_missing=False)
except modal.exception.NotFoundError:
    print("Aviso: app 'apollo-laplata' não encontrada em lookup. Vamos rodar como script standalone no contexto da engine.")

# Vamos importar a classe XttsEngine diretamente
import sys
# Adiciona o diretório raiz ao sys.path para importações locais funcionarem
sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

from backend.cloud_tools.engines.xtts_engine import XttsEngine, app

@app.local_entrypoint()
def main():
    import os
    
    ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()
        
    print("Iniciando motor XTTSv2...")
    engine = XttsEngine()
    
    texto_para_falar = "Hahaha! Nossa, isso é maravilhoso! Ahahaha! Eu não acredito que funcionou de primeira!"
    
    print(f"Gerando áudio da Matriz XTTS Fase 1...")
    
    # Chama o método remote
    audio_bytes = engine.generate_voice.remote(
        text=texto_para_falar,
        reference_audio_bytes=ref_bytes,
        language="pt",
        temperature=0.75,
        speed=1.0
    )
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "xtts_fase1_mulher_alegria.wav")
    
    with open(save_path, "wb") as f:
        f.write(audio_bytes)
        
    print(f"SUCESSO! Áudio salvo em: {save_path}")
    os.startfile(save_path)
