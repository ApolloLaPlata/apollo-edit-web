import modal
import os
import base64
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando Teste: Vocal Perfeito em PT-BR (Baseado no Perplexity)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    DURACAO = 120 # 2 Minutos 
    PASSOS = 64 # High Quality
    
    # 1. TAGS COM IDENTIDADE BR E TIMBRE VOCAL:
    estilo = "brazilian trap, dark, heavy 808s, fast hi-hats, club reverb, autotuned male rap vocals, melodic singing hooks, brazilian portuguese lyrics, rio de janeiro accent, 140 bpm, hi-fi, wide stereo"
    
    # 2. LETRAS COM MARCADORES CANÔNICOS, INTENSIDADE E HARMONIAS:
    letra = """[pt]

[Verse]
Eu tô no corre desde cedo, mano, sem parar
A rua ensina o que a escola não consegue dar
O grave bate no meu peito, faz tremer o chão
Quem tentou me derrubar hoje tá na minha mão

[Chorus]
VOU SUBIR, VOU SUBIR, NINGUÉM PODE ME PARAR
(ninguém pode, ninguém pode)
A NOITE É NOSSA E O GRAVE VAI ESTOURAR
(vai estourar, vai estourar)"""
    
    engine = AceStep15Engine()
    
    print(f"Enviando pedido de Trap PT-BR de {DURACAO}s para as H100s na nuvem ({PASSOS} passos)...")
    
    call = engine.generate.spawn(
        style_tags=estilo,
        lyrics=letra,
        length_seconds=DURACAO,
        steps=PASSOS
    )
        
    print("\nProcesso submetido. Aguardando processamento...")
    
    try:
        result = call.get()
        if result["status"] == "success":
            audio_bytes = base64.b64decode(result["audio_base64"])
            out_path = f"LABORATORIO_MODAIS/testes_audio/ACE_Vocal_Perfeito_PTBR_Trap.wav"
            
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"[SUCESSO] Salvo em: {out_path} (Tempo de GPU: {result.get('render_time_seconds')}s)")
        else:
            print(f"[FALHA] Erro: {result.get('error')}")
            
    except Exception as e:
        print(f"[FALHA CRITICA]: {e}")
