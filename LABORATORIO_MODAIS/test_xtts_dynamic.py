import modal
import os
import time
import sys

# Injetar o path para achar a pasta raiz backend/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.audio_stitcher import TTSPolicyEngine

@app.local_entrypoint()
def main():
    from backend.cloud_tools.engines.xtts_engine import XttsEngine
    
    print("Iniciando Bateria de Testes Dinâmicos (Policy Engine) no XTTSv2...")
    engine = XttsEngine()
    
    # 1. Carregar arquivo de referência neutro
    ref_audio_path = "teste_kokoro.wav"
    if not os.path.exists(ref_audio_path):
        print(f"❌ Erro: Áudio de referência {ref_audio_path} não encontrado!")
        return
        
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()

    timestamp = int(time.time())
    
    # Cenas para teste
    test_cases = [
        {
            "id": "neutro",
            "text": "O conselho de administração aprovou hoje a nova fusão de empresas. Especialistas dizem que o impacto no mercado será mínimo.",
            "emotion": "neutral",
            "arousal": "medium",
            "pace": "normal"
        },
        {
            "id": "raivoso",
            "text": "Cara, eu simplesmente não acredito nisso! Mas que absurdo! Vocês acham que somos palhaços ou o quê?!",
            "emotion": "angry",
            "arousal": "high",
            "pace": "fast"
        },
        {
            "id": "triste",
            "text": "Eu... eu só fiquei olhando. Não tinha o que fazer... a casa inteira caiu em silêncio.",
            "emotion": "sad",
            "arousal": "low",
            "pace": "slow"
        },
        {
            "id": "ironico",
            "text": "Ah, claro... O governo realmente vai resolver os nossos problemas agora. Nossa, que alívio gigantesco...",
            "emotion": "ironic",
            "arousal": "medium",
            "pace": "slow"
        }
    ]
    
    for case in test_cases:
        print(f"\n[Gerando Teste] Persona: {case['emotion'].upper()} | Text: {case['text'][:40]}...")
        
        # Pega os parâmetros ideais matemáticos para essa emoção via a Policy Engine!
        params = TTSPolicyEngine.get_params(case['emotion'], case['arousal'], case['pace'])
        print(f"Parâmetros mapeados: {params}")
        
        # Chama a nuvem com os novos parâmetros super refinados
        out_bytes = engine.generate_voice.remote(
            text=case["text"], 
            reference_audio_bytes=ref_bytes, 
            temperature=params["temperature"], 
            speed=params["speed"],
            language="pt",
            repetition_penalty=params["repetition_penalty"]
        )
        
        filename = f"xtts_policy_test_{case['id']}_{timestamp}.wav"
        with open(filename, "wb") as f:
            f.write(out_bytes)
            
        print(f"✅ Salvo como {filename}")
        
    print("\n✅ BATERIA DE TESTES POLICY ENGINE CONCLUÍDA!")
