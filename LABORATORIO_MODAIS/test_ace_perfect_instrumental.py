import modal
import os
import base64
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando Teste: Instrumental de 4 Minutos Perfeito no ACE-Step (Baseado no Perplexity)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    # 1. DURAÇÃO: 240s (O sweet spot máximo seguro da comunidade)
    DURACAO = 240 
    
    # 2. TAGS: Incluindo os reforços anti-bocejo recomendados.
    estilo = "heavy dark commercial trap beat, young thug style, deep 808 bass, crisp fast hi-hats, high quality studio mixing, dynamic beat, no vocals, no singing, purely instrumental"
    
    # 3. LETRA: Usando a tag de silêncio oficial.
    letra = "[instrumental]" 
    
    # 4. PASSOS (O GRANDE VILÃO): 64 passos (High Quality da comunidade). 1000 estava fritando os latentes.
    PASSOS = 64
    
    engine = AceStep15Engine()
    
    print(f"Enviando pedido calibrado de {DURACAO}s para as H100s na nuvem ({PASSOS} passos)...")
    
    call = engine.generate.spawn(
        style_tags=estilo,
        lyrics=letra,
        length_seconds=DURACAO,
        steps=PASSOS
    )
        
    print("\nProcesso submetido. Como baixamos os passos de 1000 para 64, isso deve gerar muito rápido!")
    
    try:
        result = call.get()
        if result["status"] == "success":
            audio_bytes = base64.b64decode(result["audio_base64"])
            import time
            timestamp = int(time.time())
            out_path = f"LABORATORIO_MODAIS/testes_audio/ACE_Instrumental_Perfeito_4Min_{timestamp}.wav"
            
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"[SUCESSO] Salvo em: {out_path} (Tempo de GPU: {result.get('render_time_seconds')}s)")
        else:
            print(f"[FALHA] Erro: {result.get('error')}")
            
    except Exception as e:
        print(f"[FALHA CRITICA]: {e}")
