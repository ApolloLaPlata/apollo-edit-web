import os
import sys
import json
import wave
import struct

sys.path.insert(0, r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

from config_manager import ConfigManager
from tts_manager import TTSManager

def main():
    print("Criando arquivo WAV de teste...")
    wav_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\scratch\dummy.wav"
    os.makedirs(os.path.dirname(wav_path), exist_ok=True)
    
    with wave.open(wav_path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(44100)
        for i in range(44100):
            value = int(32767.0 * 0) # silêncio
            data = struct.pack('<h', value)
            f.writeframesraw(data)
            
    print("Atualizando config.json temporariamente...")
    config_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
        
    config_data["personagens"]["Rafael Descargas"]["audio_ref_moss"] = wav_path
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
        
    print("Inicializando ConfigManager...")
    config = ConfigManager(config_path)
    config.workspace_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB"
    
    personagem = "Rafael Descargas" 
    
    tts = TTSManager(config)
    output = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\outputs\teste_moss_tts.mp3"
    
    print(f"Testando Geração de Áudio (Modelo 2 = MossTTS) para: {output}")
    success = tts.generate_audio(
        character_name=personagem,
        text="Olá, eu sou Rafael e estou testando o Moss TTS integrado.",
        output_path=output,
        _modelo_override=2
    )
    
    if success:
        print("✅ SUCESSO! Áudio gerado!")
    else:
        print("❌ FALHA!")

if __name__ == '__main__':
    main()