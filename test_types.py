import urllib.request, re
url = 'https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/blueprints/Image%20Edit%20(Qwen%202511).json'
data = urllib.request.urlopen(url).read().decode('utf-8')
types = re.findall(r'\"type\":\s*\"([^\"]+)\"', data)
for t in set(types):
    print(t)
