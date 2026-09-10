import os
import time
import base64
import modal

app = modal.App("minimax-stress-vocal")

@app.local_entrypoint()
def main():
    from backend.cloud_tools.engines.minimax_engine import MinimaxEngine
    engine = MinimaxEngine()
    
    os.makedirs("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    t = {
        "nome": "Vocal_Pro_BR",
        "prompt": "[Language: Portuguese (Brazil)] [Accent: Brazilian/Paulista] Brazilian Trap music, heavy 808 sub bass, aggressive male vocals singing in Brazilian Portuguese, dark ambient pads, 140 BPM, high quality studio mix",
        "lyrics": "[Verse]\n[PT-BR]\nEntrando nas sombras da mente, olha o grave batendo na caixa.\nSem limite pra quem vem de baixo, o suor na camisa nao racha.\n[Chorus]\n[PT-BR]\nO tempo fechou, a noite e nossa!\nNinguem passa do limite, a batida destroca!\n[Verse 2]\n[PT-BR]\nSente o 808 tremendo o chao, Apollo Edit dominando o beat.\nSem recuar, sem pedir perdao, cada rima e um novo hit.\n[Chorus]\n[PT-BR]\nO tempo fechou, a noite e nossa!\nNinguem passa do limite, a batida destroca!\n[Bridge]\n[PT-BR]\nA batida e pesada, o grave destroi.\nO beat e insano, a mente corroe.\n[Chorus]\n[PT-BR]\nO tempo fechou, a noite e nossa!\nNinguem passa do limite, a batida destroca!\n[Outro]\n[PT-BR]\nFade out no grave... Apollo na mente.",
        "is_instrumental": False,
        "duration": 210.0 # 3.5 minutos
    }

    print("Iniciando TESTE VOCAL PRO no MiniMax-Music3 (H100)...")
    print(f"Executando Teste: {t['nome']}")
    
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

