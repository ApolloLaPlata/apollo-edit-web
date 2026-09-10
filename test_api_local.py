import requests

try:
    print("Testando API localmente...")
    response = requests.post("http://127.0.0.1:8000/api/audio/lab_test", data={
        "model": "sa3",
        "prompt": "teste local script"
    })
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Erro ao testar a API:", e)
