import urllib.request, json
req = urllib.request.Request('https://huggingface.co/api/models/Comfy-Org/Qwen-Image_ComfyUI/tree/main/split_files/text_encoders')
res = urllib.request.urlopen(req).read()
print(json.dumps(json.loads(res.decode('utf-8')), indent=2))
