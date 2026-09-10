import os
import time
import base64
import modal

# Conecta aa funao remota do Modal
engine = modal.Cls.lookup("apollo-minimax-engine", "MinimaxEngine")()

os.makedirs("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_audio", exist_ok=True)

testes = [
    {
        "nome": "Vocal_Pesado_BR",
        "prompt": "brazilian trap, aggressive male vocals, deep 808 bass, fast hi-hats, dark ambient pads, 140 BPM, high quality studio mix, emotional rap",
        "lyrics": "[Verse]\nEntrando nas sombras da mente, olha o grave batendo na caixa.\nSem limite pra quem vem de baixo, o suor na camisa não racha.\n[Chorus]\nO tempo fechou, a noite é nossa!\nNinguém passa do limite, a batida destroça!\n[Verse 2]\nSente o 808 tremendo o chão, Apollo Edit dominando o beat.\nSem recuar, sem pedir perdão, cada rima é um novo hit.\n[Chorus]\nO tempo fechou, a noite é nossa!\nNinguém passa do limite, a batida destroça!\n[Outro]\nFade out no grave... Apollo na mente.",
        "is_instrumental": False,
        "duration": 210.0 # 3.5 minutos
    },
    {
        "nome": "Instrumental_Eletronica",
        "prompt": "Pure Trance EDM instrumental, no vocals, no voice, 138 BPM, driving bassline, euphoric synthesizer leads, massive drop, festival anthem, fully instrumental",
        "lyrics": "", # Vazio para forar o modelo a focar no prompt
        "is_instrumental": True,
        "duration": 210.0 # 3.5 minutos
    },
    {
        "nome": "Instrumental_Acustico",
        "prompt": "Solo acoustic guitar instrumental, melancholic fingerpicking, cinematic folk, slow tempo, relaxing, no vocals",
        "lyrics": "",
        "is_instrumental": True,
        "duration": 180.0 # 3 minutos
    }
]

print("Iniciando BATERIA DE STRESS no MiniMax-Music3 (H100)...")

for t in testes:
    print(f"\n=========================================")
    print(f"Executando Teste: {t['nome']}")
    print(f"Durao alvo: {t['duration']} segundos")
    
    # Chama a API
    wav_base64 = engine.generate.remote(
        prompt=t['prompt'], 
        is_instrumental=t['is_instrumental'], 
        lyrics=t['lyrics'], 
        duration=t['duration']
    )
    
    wav_data = base64.b64decode(wav_base64)
    out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_audio/MiniMax_Stress_{t['nome']}_{int(time.time())}.wav"
    
    with open(out_path, "wb") as f:
        f.write(wav_data)
        
    print(f"Salvo em: {out_path}")

print("\nBateria de testes concluida!")
