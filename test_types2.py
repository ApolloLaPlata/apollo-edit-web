import urllib.request, json
url = 'https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/blueprints/Image%20Edit%20(Qwen%202511).json'
data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
for node in data['definitions']['subgraphs'][0]['nodes']:
    if node['id'] in [2, 7]:
        print(node['type'], node.get('widgets_values'))
