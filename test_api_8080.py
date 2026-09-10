import requests

try:
    print("Testando API localmente na porta 8080...")
    response = requests.post("http://127.0.0.1:8080/api/audio/lab_test", data={
        "model": "sa3",
        "prompt": "teste local script",
        "duration": 30
    })
    print("Status Code:", response.status_code)
    print("Response JSON:", response.text)
except Exception as e:
    print("Erro ao testar a API:", e)
