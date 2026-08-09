# -*- coding: utf-8 -*-
import requests
import json
import time

def test_voice_api():
    print("Testando /api/voice/catalog...")
    try:
        r = requests.get("http://localhost:8080/api/voice/catalog", timeout=10)
        r.raise_for_status()
        data = r.json()
        print("Catalogo:", json.dumps(data, indent=2))
        
        # Obter IDs para testar
        kokoro_voice = next((v["id"] for v in data.get("catalog", []) if v["type"] == "standard"), None)
        xtts_voice = next((v["id"] for v in data.get("catalog", []) if v["type"] == "clone"), None)
        
        if kokoro_voice:
            print(f"\nTestando geração Kokoro com {kokoro_voice}...")
            r2 = requests.post("http://localhost:8080/api/voice/generate", json={
                "text": "Teste de voz padrão funcionando.",
                "voice_id": kokoro_voice
            })
            if r2.status_code == 200:
                print(f"✅ Geração Kokoro OK: {len(r2.content)} bytes.")
                with open("test_kokoro.wav", "wb") as f:
                    f.write(r2.content)
            else:
                print(f"❌ Falha Kokoro: {r2.status_code} - {r2.text}")
                
        if xtts_voice:
            print(f"\nTestando geração XTTS com {xtts_voice}...")
            r3 = requests.post("http://localhost:8080/api/voice/generate", json={
                "text": "Teste de voz zero-shot clone.",
                "voice_id": xtts_voice
            })
            if r3.status_code == 200:
                print(f"✅ Geração XTTS OK: {len(r3.content)} bytes.")
                with open("test_xtts.wav", "wb") as f:
                    f.write(r3.content)
            else:
                print(f"❌ Falha XTTS: {r3.status_code} - {r3.text}")
                
    except Exception as e:
        print(f"Erro ao testar a API: {e}")

if __name__ == "__main__":
    # Dar uns segundos para o server subir
    time.sleep(2)
    test_voice_api()
