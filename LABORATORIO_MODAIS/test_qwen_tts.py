import os
import sys
import time
import base64

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.qwen_tts_engine import QwenTtsEngine

@app.local_entrypoint()
def run():
    print("Iniciando teste local via Modal (Qwen3-TTS Python Nativo)...")
    
    engine = QwenTtsEngine()
    
    print("Enviando requisição de geração para a Nuvem (A10G)...")
    t0 = time.time()
    
    # Podemos testar o mood enviando no 'instruct'
    res = engine.generate.remote(
        text="Olá, mestre! Eu sou a nova voz do projeto, rodando puramente em Python na velocidade da luz.",
        language="Portuguese",
        speaker="Eric",
        instruct="Alegre, animado, tom professoral e direto."
    )
    
    if res["status"] == "success":
        b64_audio = res["audio_base64"]
        audio_bytes = base64.b64decode(b64_audio)
        
        out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\output_qwen_python.wav"
        with open(out_path, "wb") as out_file:
            out_file.write(audio_bytes)
            
        print(f"SUCESSO! Áudio salvo em: {out_path}")
        print(f"Tempo total de inferência: {res['render_time_seconds']}s")
    else:
        print(f"FALHA na geração: {res['message']}")
        if "traceback" in res:
            print(res["traceback"])

if __name__ == "__main__":
    run()
