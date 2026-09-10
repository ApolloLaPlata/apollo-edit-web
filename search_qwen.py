import urllib.request, json
url = 'https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/custom-node-list.json'
data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
for n in data.get('custom_nodes', []):
    if 'Qwen' in str(n.get('reference', '')) or 'qwen' in str(n.get('reference', '')):
        print(n.get('reference'))
