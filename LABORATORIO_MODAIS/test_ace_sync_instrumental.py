import modal
import os
import base64
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando Teste: Instrumental de 4 Minutos Sincronizado (Estruturado)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    DURACAO = 240 
    PASSOS = 64
    
    estilo = "heavy dark commercial trap beat, young thug style, deep 808 bass, crisp fast hi-hats, high quality studio mixing, dynamic beat, no vocals, no singing, purely instrumental"
    
    # Letra ESTRUTURADA para o Instrumental, para a IA ter o que "ler" e não bugar o timing ao longo dos 240s
    letra = """[Intro]
[Instrumental]
[Beat Starts]

[Verse 1]
[Instrumental]
[Heavy 808]

[Pre-Chorus]
[Instrumental]
[Build up]

[Chorus]
[Instrumental Drop]
[Hard Beat]

[Verse 2]
[Instrumental]
[Hi-hats roll]

[Pre-Chorus]
[Instrumental]
[Build up]

[Chorus]
[Instrumental Drop]
[Hard Beat]

[Bridge]
[Instrumental]
[Atmospheric]

[Guitar Solo]
[Instrumental Solo]

[Chorus]
[Instrumental Drop]
[Hard Beat]

[Outro]
[Instrumental]
[Fade out]""" 
    
    engine = AceStep15Engine()
    
    print(f"Enviando pedido Instrumental Estruturado de {DURACAO}s para as H100s na nuvem ({PASSOS} passos)...")
    
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
            out_path = f"LABORATORIO_MODAIS/testes_audio/ACE_Instrumental_Sync_4Min_{timestamp}.wav"
            
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"[SUCESSO] Salvo em: {out_path} (Tempo de GPU: {result.get('render_time_seconds')}s)")
        else:
            print(f"[FALHA] Erro: {result.get('error')}")
            
    except Exception as e:
        print(f"[FALHA CRITICA]: {e}")
