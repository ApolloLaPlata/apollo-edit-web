import requests
key = "sk-lit-3d061abb-d92d-4d66-a79a-7474664caf81"
headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
payload = {"model": "nvidia-nemotron-3-ultra-550b-a55b", "messages": [{"role": "user", "content": "hello"}], "temperature": 0.7}
r = requests.post("https://lightning.ai/api/v1/chat/completions", headers=headers, json=payload)
print(f"nemotron: {r.status_code}")
print(r.text)
