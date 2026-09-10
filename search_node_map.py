import urllib.request, json
url = 'https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/extension-node-map.json'
data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
found = False
for extension_url, nodes in data.items():
    if 'Qwen2.5-VL-ModelLoader' in nodes[0]:
        print('Found ModelLoader in:', extension_url)
        found = True
    if 'TextEncodeQwenImageEditPlus' in nodes[0]:
        print('Found TextEncode in:', extension_url)
        found = True
if not found:
    print('Nodes not found in extension-node-map.json!')
