import requests
import json

admin_cfg = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\admin_config.json'
with open(admin_cfg, 'r', encoding='utf-8') as f:
    c = json.load(f)
    keys = c.get('api_config', {}).get('lightning_chat', {}).get('api_keys', [])

key = keys[1] 
headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
payload = {
    'model': 'openai/gpt-5-mini',
    'messages': [{'role': 'user', 'content': 'hello'}],
    'temperature': 0.7
}
r = requests.post('https://lightning.ai/api/v1/chat/completions', headers=headers, json=payload)
print(r.status_code, r.text[:100])
