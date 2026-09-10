import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.cloud_tools.engines.whisper_engine import app, WhisperTurboSTT

@app.local_entrypoint()
def main():
    print("Transcrevendo...")
    engine = WhisperTurboSTT()
    
    ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\female_clean_ref.wav"
    with open(ref_audio_path, "rb") as f:
        audio_bytes = f.read()
        
    result = engine.transcribe.remote(audio_bytes, "pt")
    print(f"TRANSCRIÇÃO EXATA: {result['text']}")
