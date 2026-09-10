import modal
import os
import io
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    from backend.cloud_tools.engines.f5_engine import F5TTSEngine
    
    print("Iniciando F5-TTS na Modal...")
    engine = F5TTSEngine()
    
    # -------------------------------------------------------------
    # SETUP DO ÁUDIO DE REFERÊNCIA (Obrigatório para clonar EMOÇÃO)
    # -------------------------------------------------------------
    # 1. Devemos passar um áudio real onde o locutor demonstre a emoção
    # 2. Devemos informar exatamente o que ele diz no áudio (ref_text)
    
    ref_audio_path = "default_voice.wav"
    # ATENÇÃO: Substitua este texto pelo texto exato que é falado no default_voice.wav
    # Quanto mais preciso for o ref_text em relação ao ref_audio, melhor será a emoção clonada!
    ref_text = "Esta é a voz de referência. Substitua este texto pelo que o locutor diz no arquivo." 
    
    if not os.path.exists(ref_audio_path):
        print(f"❌ Erro: Arquivo {ref_audio_path} não encontrado no diretório local.")
        return
        
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()
        
    print(f"Gerando áudio usando referência: {ref_audio_path}...")
    texto_para_gerar = "Isto é um teste do motor F5-TTS rodando na nuvem da Modal. Estou tentando aplicar a emoção exata do áudio de referência!"
    
    # IMPORTANTE: A API F5TTSEngine().generate_voice precisa aceitar o ref_text!
    out_bytes = engine.generate_voice.remote(
        text=texto_para_gerar, 
        reference_audio_bytes=ref_bytes,
        ref_text=ref_text
    )
    
    import time
    
    output_dir = "LABORATORIO_MODAIS"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"f5_saida_teste_{int(time.time())}.ogg")
    with open(output_path, "wb") as f:
        f.write(out_bytes)
        
    print(f"✅ Sucesso! Gerou {len(out_bytes)} bytes de áudio. Arquivo salvo como: {output_path}")
