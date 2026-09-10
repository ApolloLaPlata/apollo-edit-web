import modal
import os
import base64
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando Teste: Instrumental 30s (Alta densidade de tags de silencio)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    DURACAO = 30 
    PASSOS = 64
    
    estilo = "heavy dark commercial trap beat, young thug style, deep 808 bass, crisp fast hi-hats, high quality studio mix, purely instrumental, no vocals, no singing, no spoken voice"
    
    # Preenchendo com vrias tags [inst] para dar "ancoras" temporais ao LLM sem pedir vozes
    letra = """[intro]
[inst]
[inst]
[inst]
[inst]
[inst]
[outro]"""
    
    engine = AceStep15Engine()
    
    call = engine.generate.spawn(
        style_tags=estilo,
        lyrics=letra,
        length_seconds=DURACAO,
        steps=PASSOS
    )
        
    try:
        result = call.get()
        if result["status"] == "success":
            audio_bytes = base64.b64decode(result["audio_base64"])
            import time
            timestamp = int(time.time())
            out_path = f"LABORATORIO_MODAIS/testes_audio/ACE_Inst_30s_Dense_{timestamp}.wav"
            
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"[SUCESSO] Salvo em: {out_path}")
        else:
            print(f"[FALHA] Erro: {result.get('error')}")
            
    except Exception as e:
        print(f"[FALHA CRITICA]: {e}")
