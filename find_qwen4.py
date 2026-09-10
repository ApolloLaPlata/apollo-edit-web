import urllib.request, json
req = urllib.request.Request('https://huggingface.co/api/models?search=Qwen&author=Comfy-Org')
res = urllib.request.urlopen(req).read()
for m in json.loads(res.decode('utf-8')): print(m['id'])
