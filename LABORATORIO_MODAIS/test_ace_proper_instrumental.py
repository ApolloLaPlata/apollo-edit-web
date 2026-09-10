import modal
import os
import base64
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando Teste: Instrumental Puro (Configuração Corrigida) no ACE-Step...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    # 1. CORREÇÃO DE TEMPO: 90 segundos.
    # O modelo quebra os 'positional encodings' se tentar gerar 4 minutos diretos em um unico disparo (gera 2 musicas tocando junto).
    DURACAO = 90 
    
    estilo = "heavy dark commercial trap beat, young thug style, deep 808 bass, crisp fast hi-hats, high quality studio mixing, dynamic beat"
    
    # 2. CORREÇÃO DO MUMBLING (VOZES FANTASMAS): 
    # O modelo tem um LLM. Se passar "", ele alucina vozes murmurando. TEMOS que passar a tag "[Instrumental]".
    letra = "[Instrumental]" 
    
    engine = AceStep15Engine()
    
    print(f"Enviando pedido CORRIGIDO de {DURACAO}s para as H100s na nuvem (1000 passos)...")
    
    call = engine.generate.spawn(
        style_tags=estilo,
        lyrics=letra,
        length_seconds=DURACAO,
        steps=1000
    )
        
    print("\nProcesso submetido. Aguardando retorno...")
    
    try:
        result = call.get()
        if result["status"] == "success":
            audio_bytes = base64.b64decode(result["audio_base64"])
            out_path = f"LABORATORIO_MODAIS/testes_audio/ACE_Instrumental_Corrigido_90s.wav"
            
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"[SUCESSO] Salvo em: {out_path} (Tempo de GPU: {result.get('render_time_seconds')}s)")
        else:
            print(f"[FALHA] Erro: {result.get('error')}")
            
    except Exception as e:
        print(f"[FALHA CRITICA]: {e}")
