import requests
import json

admin_cfg = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\admin_config.json"
with open(admin_cfg, 'r', encoding='utf-8') as f:
    c = json.load(f)
    keys = c.get("api_config", {}).get("lightning_chat", {}).get("api_keys", [])

print(f"Encontradas {len(keys)} chaves para testar.\n")

for i, k in enumerate(keys):
    print(f"--- TESTANDO CHAVE {i+1} ({k[:15]}...) ---")
    headers = {"Authorization": f"Bearer {k}", "Content-Type": "application/json"}
    
    # Testando com o modelo Nemotron que verificamos funcionar
    payload = {
        "model": "nvidia-nemotron-3-ultra-550b-a55b",
        "messages": [{"role": "user", "content": "hello"}],
        "temperature": 0.7
    }
    
    try:
        r = requests.post("https://lightning.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            print("Resultado: SUCESSO (Chave Ativa)")
        else:
            print(f"Erro: {r.text.strip()}")
    except Exception as e:
        print(f"Falha na conexao: {e}")
    print("")

