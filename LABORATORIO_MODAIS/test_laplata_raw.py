import requests
import json

url = 'https://apollolaplata--apollo-render-router-apollo-api.modal.run/generate/image'
payload = {'prompt': 'Portrait of Nicolas Maduro in cyberpunk style, highly detailed', 'model': 'flux2-universal', 'format': 'horizontal', 'seed': 42}
try:
    print("Testing:", url)
    res = requests.post(url, json=payload, stream=True)
    for line in res.iter_lines():
        if line:
            print(f'RAW LINE: {line}')
            try:
                print(f'PARSED: {json.loads(line)}')
            except Exception as e:
                print("JSON ERR:", e)
except Exception as e:
    print(f'Error: {e}')
