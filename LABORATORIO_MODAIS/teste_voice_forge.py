import os
import requests
import base64
import time
import json
import sys

# Corrige problema de encoding no console Windows (para rodar via subprocess)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Adiciona o diretório atual ao path para importar modulos locais
WORKSPACE_DIR = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB"
if WORKSPACE_DIR not in sys.path:
    sys.path.append(WORKSPACE_DIR)

from config_manager import ConfigManager
from gemini_tts_api import GeminiTTSProvider

# === CONFIGURAÇÕES ===
XTTS_MODAL_URL = "https://apollolaplata--apollo-api-xtts.modal.run"
OUT_PATH_GEMINI = r"C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\voice_forge_gemini_base.wav"
OUT_PATH_FINAL = r"C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\voice_forge_xtts_final.ogg"

# Textos e Emoção
texto = "Eu não acredito! Você destruiu tudo que a gente construiu nesses últimos cinco anos! Você é um idiota!"
instrucao_emocao = "Grite com muito ódio e decepção, chorando"
gemini_voice = "Puck" # Voz nativa do Gemini (Aoede, Charon, Fenrir, Kore, Puck)

def run_voice_forge():
    print("🚀 Iniciando Voice Forge Pipeline (Gemini TTS -> XTTS)...")
    
    config = ConfigManager(os.path.join(WORKSPACE_DIR, "config.json"))
    gemini_tts = GeminiTTSProvider(config)
    
    # 1. Obter voz do Gemini para Emoção Base
    print(f"\n[Passo 1] Solicitando áudio emocional base do Gemini TTS (Voz: {gemini_voice})...")
    print(f"Instrução: {instrucao_emocao}")
    
    start_time = time.time()
    
    success = gemini_tts.generate_tts(
        text=texto,
        voice_id=gemini_voice,
        output_path=OUT_PATH_GEMINI,
        instruction_prompt=instrucao_emocao
    )
    
    if not success or not os.path.exists(OUT_PATH_GEMINI):
        print("❌ Falha ao gerar áudio base com Gemini TTS.")
        return
        
    print(f"✅ Áudio Gemini (Emoção Base) gerado com sucesso!")
    
    # Lendo os bytes gerados
    with open(OUT_PATH_GEMINI, "rb") as f:
        gemini_bytes = f.read()

    # 2. Enviar para XTTS Modal (Clonagem de Emoção em PT-BR)
    print(f"\n[Passo 2] Enviando áudio base (emoção) para XTTS Modal para clonagem no personagem final...")
    ref_b64 = base64.b64encode(gemini_bytes).decode('utf-8')
    
    try:
        r_xtts = requests.post(XTTS_MODAL_URL, json={
            "text": texto,
            "ref_audio_base64": ref_b64
        }, timeout=120)
        
        duration = time.time() - start_time
        if r_xtts.status_code == 200:
            with open(OUT_PATH_FINAL, "wb") as f:
                f.write(r_xtts.content)
            print(f"\n✅ SUCESSO ABSOLUTO! Voice Forge finalizado em {duration:.2f}s")
            print(f"📁 Áudio final salvo em: {OUT_PATH_FINAL}")
        else:
            print(f"❌ Falha no XTTS Modal: {r_xtts.status_code} - {r_xtts.text}")
    except Exception as e:
        print(f"❌ Erro de conexão com XTTS Modal: {e}")

if __name__ == "__main__":
    run_voice_forge()
