# -*- coding: utf-8 -*-
import requests
import json
import os
import time
import base64

URL = 'https://radiodarktrap--apollo-render-router-apollo-api.modal.run/generate/audio_lab'
OUTPUT_DIR = 'testes_musica_conta9'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_test(name, prompt, model, duration=10):
    print(f'\n--- Gerando: {name} ---')
    print(f'Prompt completo:\n{prompt}')
    payload = {
        'prompt': prompt,
        'model': model,
        'duration': duration
    }
    try:
        t0 = time.time()
        resp = requests.post(URL, json=payload, timeout=600)
        resp.raise_for_status()
        
        lines = [line for line in resp.text.split('\n') if line.strip()]
        last_json = json.loads(lines[-1])
        
        audio_b64 = last_json.get('audio_base64')
        if audio_b64:
            filename = os.path.join(OUTPUT_DIR, f'{name}.mp3')
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(audio_b64))
            print(f'>> SUCESSO! {time.time()-t0:.1f}s. Salvo como {filename}')
        else:
            print(f'>> ERRO: Base64 nao encontrado.')
            
    except Exception as e:
        print(f'>> ERRO: {e}')

# TESTE 1: MODO INSTRUMENTAL (SIMPLES)
estilos_inst = [
    "Dark Trap beat, 808 bass, fast hi-hats",
    "Lo-fi hip hop, chill, vinyl crackle",
    "Epic orchestral cinematic trailer music"
]

print("=== INICIANDO TESTE 1: MODO INSTRUMENTAL ===")
for i, estilo in enumerate(estilos_inst):
    # Lógica exata do Javascript para modo instrumental
    p = estilo + ", instrumental, no vocals, purely instrumental"
    run_test(f"lote_inst_{i+1}", p, "sa3", 5)

# TESTE 2: MODO VOCAL (DUPLO)
estilos_vocal = [
    "Pop punk, fast tempo, energetic",
    "R&B smooth, slow jam",
    "Heavy Metal, aggressive guitars"
]
letras_vocal = [
    "[Verse]\nWaking up so late\n[Chorus]\nBut I don't care today!",
    "[Verse]\nYou looked at me\n[Chorus]\nOh baby let it be",
    "[Verse]\nFire in the sky\n[Chorus]\nWatch it all burn down!"
]

print("\n=== INICIANDO TESTE 2: MODO VOCAL COM LETRAS ===")
for i, estilo in enumerate(estilos_vocal):
    # Lógica exata do Javascript para modo vocal
    p = estilo + ", vocals, singing, lyrics, singer"
    if i < len(letras_vocal):
        p += "\n\nLyrics:\n" + letras_vocal[i]
    run_test(f"lote_vocal_{i+1}", p, "minimax", 5)

print("\nTODOS OS TESTES CONCLUIDOS!")
