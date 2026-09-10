import modal
import os
import time

# Precisamos injetar o path para achar a pasta raiz backend/
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    from backend.cloud_tools.engines.xtts_engine import XttsEngine
    
    print("Iniciando Bateria de Testes Extremistas no XTTSv2...")
    engine = XttsEngine()
    
    # 1. Carregar arquivo de referência
    # Vamos usar default_voice.wav que está na pasta LABORATORIO_MODAIS, se não achar, tentar na raiz
    ref_audio_path = "default_voice.wav"
    if not os.path.exists(ref_audio_path):
        ref_audio_path = "../default_voice.wav"
        
    if not os.path.exists(ref_audio_path):
        print(f"❌ Erro: Áudio de referência não encontrado!")
        return
        
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()

    output_dir = "."
    timestamp = int(time.time())

    # ==============================================================
    # TESTE 1: SOTAQUE CRUZADO (Forçando inglês em texto PT)
    # ==============================================================
    print("\n[Teste 1] Sotaque Cruzado (Lang=EN, Texto=PT)...")
    texto_pt_en = "I can't believe this! Você não sabe o que acabou de acontecer! This is crazy!"
    out_1 = engine.generate_voice.remote(
        text=texto_pt_en, 
        reference_audio_bytes=ref_bytes, 
        temperature=0.75, 
        speed=1.0,
        language="en"
    )
    with open(f"xtts_teste1_sotaquecruzado_{timestamp}.wav", "wb") as f:
        f.write(out_1)
        
    # ==============================================================
    # TESTE 2: EMOÇÕES IN-TEXT (Colchetes e Marcações)
    # ==============================================================
    print("\n[Teste 2] Emoções In-Text (Lang=PT)...")
    texto_in_text = "[laughs] Eu simplesmente não acredito nisso! [sighs] Mas que loucura... [angry] EU NÃO VOU ACEITAR ISSO!"
    out_2 = engine.generate_voice.remote(
        text=texto_in_text, 
        reference_audio_bytes=ref_bytes, 
        temperature=0.75, 
        speed=1.0,
        language="pt"
    )
    with open(f"xtts_teste2_intext_{timestamp}.wav", "wb") as f:
        f.write(out_2)

    # ==============================================================
    # TESTE 3: PONTO DE FUGA (Temperatura e Velocidade Extremas)
    # ==============================================================
    print("\n[Teste 3] Ponto de Fuga (Temp=1.0, Speed=1.1, Lang=PT)...")
    texto_caos = "O cachorro correu atrás do gato, pulou o muro, caiu na piscina e todo mundo começou a rir desesperadamente sem parar um segundo sequer!"
    out_3 = engine.generate_voice.remote(
        text=texto_caos, 
        reference_audio_bytes=ref_bytes, 
        temperature=1.0,  # Máxima criatividade/Variação fonética
        speed=1.1,        # Acelerado para dar sensação de urgência
        language="pt"
    )
    with open(f"xtts_teste3_extremo_{timestamp}.wav", "wb") as f:
        f.write(out_3)
        
    print("\n✅ BATERIA DE TESTES CONCLUÍDA COM SUCESSO!")
    print("Os arquivos WAV foram salvos no diretório LABORATORIO_MODAIS para a sua avaliação.")
