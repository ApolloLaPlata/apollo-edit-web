import modal
import os
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    from backend.cloud_tools.engines.xtts_engine import XttsEngine
    
    print("Iniciando Bateria de Testes V2 (Retorno às Origens) no XTTSv2...")
    engine = XttsEngine()
    
    ref_audio_path = "teste_kokoro.wav"
    if not os.path.exists(ref_audio_path):
        print("❌ Erro: Áudio de referência não encontrado!")
        return
        
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()

    timestamp = int(time.time())
    
    # Voltamos para a estratégia que DEU CERTO: 
    # Usar TAGS DE TEXTO explícitas e Temperaturas altas (0.75 a 1.0)
    test_cases = [
        {
            "id": "tags_triste",
            "text": "[sighs] Eu... eu simplesmente não sei o que fazer. [cries] Tudo deu errado hoje.",
            "temperature": 0.85, # Temp mais alta pra forçar a quebra da voz
            "speed": 1.0
        },
        {
            "id": "tags_raiva",
            "text": "[angry] Mas que inferno! Você acha que pode me tratar assim?! [screams] SAI DAQUI AGORA!",
            "temperature": 0.90, # Quase no ponto de fuga
            "speed": 1.1       # Acelerado
        },
        {
            "id": "tags_ironia",
            "text": "[laughs] Ai ai... você é realmente um gênio, sabia? [smirks] Parabéns pela ideia brilhante.",
            "temperature": 0.80,
            "speed": 1.0
        }
    ]
    
    for case in test_cases:
        print(f"\n[Gerando Teste] ID: {case['id']} | Temp: {case['temperature']} | Speed: {case['speed']}")
        print(f"Texto: {case['text']}")
        
        out_bytes = engine.generate_voice.remote(
            text=case["text"], 
            reference_audio_bytes=ref_bytes, 
            temperature=case["temperature"], 
            speed=case["speed"],
            language="pt"
        )
        
        filename = f"xtts_origens_{case['id']}_{timestamp}.wav"
        with open(filename, "wb") as f:
            f.write(out_bytes)
            
        print(f"✅ Salvo como {filename}")
        
    print("\n✅ BATERIA DE TESTES ORIGINAIS CONCLUÍDA!")
