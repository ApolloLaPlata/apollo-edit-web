import requests
import json

url = "https://apollolaplata--apollo-api-transcribe-dev.modal.run"
file_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    
if response.status_code == 200:
    print(response.json()["text"])
else:
    print(f"Error: {response.text}")
