import os
import sys

# Adiciona o diretório raiz para importar o motor
sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")
from backend.cloud_tools.engines.elevenlabs_engine import ElevenLabsEngine

def main():
    # 1. Pegar a chave (pode ser via variável de ambiente ou injetada aqui)
    API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
    if not API_KEY:
        API_KEY = input("Cole sua API KEY da ElevenLabs (sk_...): ").strip()
        
    if not API_KEY:
        print("Erro: API Key não fornecida.")
        return

    # 2. Inicializar Motor
    engine = ElevenLabsEngine(api_key=API_KEY)
    
    # 3. Referência
    ref_audio = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"
    if not os.path.exists(ref_audio):
        print(f"Erro: Arquivo base não encontrado: {ref_audio}")
        return
        
    # 4. Criar a voz (O Clone)
    voice_name = "Mulher Base - Extracao Emocional"
    print("Iniciando Fase 1 - O Assalto na ElevenLabs")
    voice_id = engine.clone_voice(
        name=voice_name,
        description="Clonagem Temporária para gerar Matrizes",
        file_paths=[ref_audio]
    )
    
    # 5. O Cofre de Matrizes
    matrizes = {
        "alegria": "Hahaha! Nossa, que maravilha! Ahahaha! Eu não acredito que isso funcionou tão bem!",
        "raiva": "Grrr! Mas que inferno! Eu não aguento mais isso, que ódio!",
        "tristeza": "Ah... isso é tão triste... não acredito que acabou assim... snif...",
        "susto": "Ah! Meu Deus... o que foi isso?! Que susto!",
        "neutra": "A temperatura ambiente hoje está amena, com chances de chuva."
    }
    
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\elevenlabs"
    os.makedirs(save_dir, exist_ok=True)
    
    print("\n[INICIO] Gerando os 5 estados emocionais...")
    
    # 6. Gerar e Salvar cada emoção
    for emocao, texto in matrizes.items():
        print(f"-> Gerando Matriz: {emocao.upper()}")
        audio_bytes = engine.generate_voice(text=texto, voice_id=voice_id)
        
        save_path = os.path.join(save_dir, f"matriz_{emocao}.mp3")
        with open(save_path, "wb") as f:
            f.write(audio_bytes)
        print(f"   Salvo: {save_path}")
        
    # 7. Apagar a voz da ElevenLabs (Limpando as pistas do Assalto)
    print("\n[LIXEIRA] Limpando a voz da nuvem para evitar cobranças/limites extras...")
    engine.delete_voice(voice_id=voice_id)
    
    print("\n[SUCESSO] Operação concluída! Seus áudios estão em:")
    print(save_dir)

if __name__ == "__main__":
    main()
