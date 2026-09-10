import os
import sys
import modal

# Adiciona o diretório raiz ao sys.path para importações locais funcionarem
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
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()
        
    print("Iniciando Fish Speech 1.5 para teste de Humor...")
    engine = FishTTSEngine()
    
    # Texto com marcações claras de humor
    texto_para_falar = "Hahaha! Nossa, que maravilha! Ahahaha! Eu não acredito que isso funcionou tão bem!"
    
    print("Enviando pedido para a GPU na nuvem...")
    audio_bytes = engine.generate_voice.remote(
        text=texto_para_falar,
        reference_audio_bytes=ref_bytes
    )
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "fish_teste_mulher_alegria.wav")
    
    with open(save_path, "wb") as f:
        f.write(audio_bytes)
        
    print(f"SUCESSO! Áudio Fish Speech salvo em: {save_path}")
    os.startfile(save_path)
