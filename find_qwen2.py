import urllib.request
import json
req = urllib.request.Request('https://huggingface.co/api/models?search=Qwen2.5-VL&sort=downloads&direction=-1&limit=10')
res = urllib.request.urlopen(req).read()
for m in json.loads(res.decode('utf-8')): print(m['id'])
