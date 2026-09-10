import modal
import os
import time
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.cloud_tools.modal_app import app

@app.function(gpu="T4")
def run_pure_test_on_cloud(ref_bytes: bytes, text: str):
    import tempfile
    from TTS.api import TTS
    import io
    import soundfile as sf
    import numpy as np
    
    print("[NUVEM] Carregando XTTS puro...")
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(ref_bytes)
        ref_file_path = f.name
        
    print("[NUVEM] Gerando áudio sem nenhum kwarg extra...")
    wav = tts.tts(text=text, speaker_wav=ref_file_path, language="pt")
    
    wav_arr = np.array(wav)
    out_io = io.BytesIO()
    sf.write(out_io, wav_arr, 24000, format='WAV', subtype='PCM_16')
    return out_io.getvalue()

@app.local_entrypoint()
def main():
    ref_audio_path = "default_voice.wav"
    if not os.path.exists(ref_audio_path):
        print("❌ Erro: Áudio de referência não encontrado!")
        return
        
    with open(ref_audio_path, "rb") as f:
        ref_bytes = f.read()
        
    texto_puro = "Este é um teste de calibração absoluta. Sem tags no texto, sem alterar temperatura ou velocidade. Se a voz falhar aqui e ficar com chiadeira, o problema é o arquivo de áudio base."
    print("Chamando função pura na nuvem...")
    out_bytes = run_pure_test_on_cloud.remote(ref_bytes, texto_puro)
    
    timestamp = int(time.time())
    filename = f"xtts_puro_nativo_{timestamp}.wav"
    with open(filename, "wb") as f:
        f.write(out_bytes)
    print(f"✅ Salvo como {filename}")
