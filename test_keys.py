import requests
import json

admin_cfg = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\admin_config.json"
with open(admin_cfg, 'r', encoding='utf-8') as f:
    c = json.load(f)
    keys = c.get("api_config", {}).get("lightning_chat", {}).get("api_keys", [])

for k in keys:
    print(f"Testando {k[:15]}...")
    headers = {"Authorization": f"Bearer {k}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "messages": [{"role": "user", "content": "hello"}],
        "temperature": 0.7
    }
    r = requests.post("https://lightning.ai/api/v1/chat/completions", headers=headers, json=payload)
    print(r.status_code, r.text)
