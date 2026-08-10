import os
import modal
import base64

# Laboratório XTTS Puro - Teste de Extremos Emocionais
# Vamos gerar 4 áudios testando a gramática e a temperatura (sem modelo secundário)

def run_tests():
    # Referência neutra padrão (substitua por um path real se tiver)
    ref_path = "public/reference_audio.wav"
    
    if not os.path.exists(ref_path):
        print(f"ERRO: Não encontrei {ref_path}. Por favor, crie ou altere este caminho para rodar o laboratório.")
        return

    with open(ref_path, "rb") as f:
        ref_bytes = f.read()

    print("Invocando a classe XTTS na Nuvem Modal...")
    
    try:
        from backend.cloud_tools.engines.xtts_engine import XttsEngine
        engine = XttsEngine()
    except Exception as e:
        print("Erro ao importar XttsEngine:", e)
        return

    test_cases = [
        {"nome": "1_neutro.wav", "text": "A porta estava fechada, então eu voltei para casa.", "temp": 0.75, "speed": 1.0},
        {"nome": "2_tristeza_extrema.wav", "text": "A porta... estava fechada... eu... eu voltei para casa...", "temp": 0.50, "speed": 0.85},
        {"nome": "3_raiva_extrema.wav", "text": "A porta estava FECHADA! ENTÃO EU VOLTEI PARA CASA!!!", "temp": 0.90, "speed": 1.15},
        {"nome": "4_caotico.wav", "text": "A porta... FECHADA!? Voltei pra casa!!!", "temp": 1.0, "speed": 1.1}
    ]

    for case in test_cases:
        print(f"-> Gerando {case['nome']} (Temp: {case['temp']}, Speed: {case['speed']})")
        print(f"   Texto: {case['text']}")
        try:
            # Chama a função remota na GPU
            audio_bytes = engine.generate_voice.remote(
                case["text"], 
                ref_bytes, 
                temperature=case["temp"], 
                speed=case["speed"]
            )
            
            with open(case["nome"], "wb") as f:
                f.write(audio_bytes)
            print(f"   [OK] Salvo como {case['nome']}")
        except Exception as e:
            print(f"   [ERRO] Falha ao gerar: {e}")

if __name__ == '__main__':
    run_tests()
