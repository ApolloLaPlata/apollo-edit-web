import urllib.request, struct, json
req = urllib.request.Request('https://huggingface.co/TingFengYu/qwen_2.5_vl_7b_fp8_scaled.safetensors/resolve/main/qwen_2.5_vl_7b_fp8_scaled.safetensors', headers={'Range': 'bytes=0-10000'})
res = urllib.request.urlopen(req).read()
length = struct.unpack('<Q', res[:8])[0]
header = json.loads(res[8:8+length].decode('utf-8'))
print(list(header.keys())[:20])
