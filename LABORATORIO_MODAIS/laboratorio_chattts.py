import sys
import os

# Ajustar o sys.path para encontrar a pasta backend (pois o script está na subpasta LABORATORIO_MODAIS)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.cloud_tools.engines.chat_tts_engine import ChatTTSEngine, app
import modal

@app.local_entrypoint()
def main():
    print("Iniciando motor ChatTTS Oficial do Apollo...")
    engine = ChatTTSEngine()
    
    # Remoção de TODOS os acentos e pontuações complexas para evitar o balbuciamento (o modelo descarta caracteres desconhecidos).
    # Uso explícito de prompt emocional interno do ChatTTS para FORÇAR a risada e alegria.
    texto_pt = "Uau. Isso e incrivel. [laugh] Eu nao posso acreditar que funcionou tao bem. [laugh]"
    print(f"Gerando matriz emocional bruta (Português Limpo): {texto_pt}")
    
    # Parametros para forçar muita emoção/risada:
    # refine_prompt: [oral_2] (mais expressivo), [laugh_0] (risada alta), [break_4] (pausas rítmicas)
    audio_bytes = engine.generate_audio.remote(
        text=texto_pt,
        temperature=0.7, # Mais criativo e expressivo
        refine_prompt='[oral_2][laugh_0][break_4]'
    )
    
    # Salvar na pasta correta do Laboratório de Modais
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "chattts_emocao_alegria.wav")
    
    with open(save_path, "wb") as f:
        f.write(audio_bytes)
        
    print(f"SUCESSO! Áudio salvo para o XTTS em: {save_path}")
    
    # Tocar o áudio automaticamente
    os.startfile(save_path)
