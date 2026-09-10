import urllib.request
import json
req = urllib.request.Request('https://huggingface.co/api/models?search=Qwen2.5-VL-7B-Instruct')
res = urllib.request.urlopen(req).read()
print(json.loads(res.decode('utf-8'))[0]['id'])
